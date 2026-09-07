"""Outcome-blind First Hold features using only completed same-session prefixes."""
from datetime import timedelta
from decimal import Decimal, localcontext
from types import SimpleNamespace

from spy_research.break_hold.executable_reference import signal_adapter
from spy_research.events.ema_cross import detect_session_ema_crosses
from spy_research.indicators.atr import calculate_session_atr
from spy_research.indicators.ema import EMA_CONTEXT, calculate_session_ema
from spy_research.indicators.vwap import calculate_session_vwap
from spy_research.interactions.models import AvailableLevel, LevelType
from spy_research.strategy.comparisons.ema_alignment import annotate_ema_alignment
from spy_research.strategy.comparisons.ema9_vwap_alignment import annotate_ema9_vwap_alignment
from spy_research.strategy.comparisons.ema20_vwap_alignment import annotate_ema20_vwap_alignment
from spy_research.strategy.comparisons.vwap_alignment import annotate_vwap_alignment
from spy_research.strategy.comparisons.market_condition import calculate_market_condition_annotations
from spy_research.strategy.comparisons.room_to_level import select_room_to_next_level
from spy_research.strategy.comparisons.market_structure import annotate_market_structure, detect_confirmed_swings


def extract_first_hold_features(signal, bars, session):
    """No eventual label, event state, reclaim, or outcome is accepted by this API."""
    if signal.entry_style!='FIRST_HOLD' or signal.session_date!=session.session_date:
        raise ValueError('features require a First Hold in the exact session')
    visible=tuple(b for b in bars if b.timestamp+timedelta(minutes=5)<=signal.timestamp)
    if not visible or visible[-1].timestamp+timedelta(minutes=5)!=signal.timestamp:
        raise ValueError('exact completed confirmation row unavailable')
    expected=tuple(session.market_open+timedelta(minutes=5*i) for i in range(len(visible)))
    if tuple(b.timestamp for b in visible)!=expected or any(b.session_date!=session.session_date for b in visible):
        raise ValueError('feature prefix must be consecutive and same-session')
    current=visible[-1]
    if current.close!=signal.price:
        raise ValueError('canonical signal close differs from confirmation close')
    level=visible[0].high if signal.direction=='LONG' else visible[0].low
    adapter=signal_adapter(signal,session.market_close,level)
    ema=calculate_session_ema(visible)
    atr=calculate_session_atr(visible)
    vwap=calculate_session_vwap(visible)
    annotation=calculate_market_condition_annotations(SimpleNamespace(candidates=(adapter,)),visible,ema,vwap,atr)[0]
    known=tuple(AvailableLevel(session_date=signal.session_date,level_type=LevelType(l.name),level_price=l.price,
                available_from_timestamp=l.available_at) for l in signal.context.known_levels)
    room=select_room_to_next_level(adapter,confirmation_price=current.close,entry_price=None,atr14=atr[-1].atr14,levels=known)
    structure=annotate_market_structure(adapter,confirmation_close=current.close,atr14=atr[-1].atr14,
                swings=detect_confirmed_swings(visible),room=room)
    sign=Decimal(1) if signal.direction=='LONG' else Decimal(-1)
    crosses=detect_session_ema_crosses(ema)
    last=crosses[-1] if crosses else None
    cross_state=('NO_PRIOR_CROSS' if last is None else 'MATCHING_CROSS' if last.direction.value==('BULLISH' if sign==1 else 'BEARISH') else 'OPPOSING_CROSS')
    opposite=[b.timestamp+timedelta(minutes=5) for b in visible[1:]
              if (b.low<visible[0].low if sign==1 else b.high>visible[0].high)]
    opposite_state=('NO_OPPOSITE_BREAK_BY_SIGNAL' if not opposite else 'BOTH_BROKEN_BEFORE_SIGNAL_CLOSE'
                    if min(opposite)<signal.timestamp else 'OPPOSITE_FIRST_OBSERVED_THIS_CLOSE')
    with localcontext(EMA_CONTEXT):
        size=current.high-current.low
        body=current.close-current.open
        prior=visible[-7:-1]
        relative=Decimal(current.volume)/(sum(Decimal(b.volume) for b in prior)/6) if len(prior)==6 and sum(b.volume for b in prior)>0 else None
        beyond=sign*(current.close-level)
        normalized=beyond/atr[-1].atr14 if atr[-1].atr14 is not None and atr[-1].atr14>0 else None
        numeric={
            'opening_range_width':visible[0].high-visible[0].low,
            'body_size':abs(body),'directional_body':sign*body,'candle_range':size,
            'body_range_ratio':abs(body)/size if size else None,
            'directional_body_range_ratio':sign*body/size if size else None,
            'close_location':(current.close-current.low)/size if size else None,
            'directional_close_location':((current.close-current.low) if sign==1 else (current.high-current.close))/size if size else None,
            'distance_beyond_level':beyond,'distance_beyond_level_atr14':normalized,
            'candle_volume':Decimal(current.volume),'relative_volume_prior_6':relative,'atr14':atr[-1].atr14,
            'minutes_since_open':Decimal(signal.context.minutes_since_open),
            'minutes_since_ema_cross':Decimal(int((signal.timestamp-last.timestamp-timedelta(minutes=5)).total_seconds()//60)) if last else None,
            'break_attempt_rank':Decimal(signal.context.prior_break_attempts+1),
            'valid_hold_sequence_rank':Decimal(signal.context.prior_valid_holds+1),
        }
    numeric.update({'stage10_9.'+f.name:f.value for f in annotation.features})
    room_fields=('room_from_confirmation','room_in_atr','number_of_known_levels_above','number_of_known_levels_below',
                 'nearest_level_distance_above','nearest_level_distance_below','directional_level_count_within_0_5_atr','directional_level_count_within_1_0_atr')
    numeric.update({'stage11_2.'+f:Decimal(getattr(room,f)) if getattr(room,f) is not None else None for f in room_fields})
    structure_fields=('confirmation_close_to_latest_swing_high','confirmation_close_to_latest_swing_low','distance_to_swing_high_in_atr','distance_to_swing_low_in_atr')
    numeric.update({'stage11_3.'+f:getattr(structure,f) for f in structure_fields})
    categorical={
        'direction':signal.direction,'time_bucket':signal.context.time_bucket,
        'ema9_20_alignment':annotate_ema_alignment(adapter,ema[-1]).alignment_state.value,
        'price_vwap_alignment':annotate_vwap_alignment(adapter,current,vwap[-1]).alignment_state.value,
        'ema9_vwap_alignment':annotate_ema9_vwap_alignment(adapter,ema[-1],vwap[-1]).alignment_state.value,
        'ema20_vwap_alignment':annotate_ema20_vwap_alignment(adapter,ema[-1],vwap[-1]).alignment_state.value,
        'prior_ema_cross':cross_state,'opposite_boundary_broken':opposite_state,
        'stage11_2.room_bucket':room.room_bucket.value,
        'known_level_coverage':'PARTIAL_UNAVAILABLE' if signal.context.unavailable_levels else 'COMPLETE_V1_UNIVERSE',
        'stage11_3.structure':structure.combined_structure.value,
        'stage11_3.agreement':structure.direction_agreement.value,
        'stage11_3.high_structure':structure.high_structure.value,
        'stage11_3.low_structure':structure.low_structure.value,
        'stage11_3.structural_room':structure.structural_room_state.value,
        'stage11_1.regime':'UNAVAILABLE_CALIBRATION_PROVENANCE',
    }
    return dict(event_id=signal.event_id,session_date=signal.session_date,direction=signal.direction,
        signal_known_at=signal.timestamp,confirmation_bar_timestamp=current.timestamp,
        latest_input_known_at=current.timestamp+timedelta(minutes=5),visible_bar_n=len(visible),
        numeric=numeric,categorical=categorical,
        unavailable_reasons={name:'WARMUP_OR_ZERO_DENOMINATOR_OR_NO_VISIBLE_CONTEXT' for name,value in numeric.items() if value is None},
        feature_version='first_hold_prefix_only_v1')
