import { Box, Typography, Stepper, Step, StepLabel, StepContent, Chip } from '@mui/material';
import { SignalEvent } from '../../../types/domain';
import { CheckCircle2, Clock, Zap, Target, ShieldAlert, XCircle } from 'lucide-react';

interface SignalLifecycleTimelineProps {
  events: SignalEvent[];
  currentStatus: string;
}

const getStepIcon = (type: string) => {
  switch (type) {
    case 'GENERATED': return <Clock size={16} />;
    case 'VALIDATED': return <CheckCircle2 size={16} />;
    case 'ENTRY_TRIGGERED': return <Zap size={16} />;
    case 'POSITION_ACTIVE': return <Target size={16} />;
    case 'TARGET_HIT': return <Target size={16} className="text-emerald-500" />;
    case 'STOP_LOSS': return <ShieldAlert size={16} className="text-rose-500" />;
    case 'EXPIRED': return <XCircle size={16} className="text-slate-500" />;
    default: return <Clock size={16} />;
  }
};

export default function SignalLifecycleTimeline({ events, currentStatus }: SignalLifecycleTimelineProps) {
  if (!events || events.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center', opacity: 0.5 }}>
        <Typography variant="body2">No lifecycle events recorded for this signal.</Typography>
      </Box>
    );
  }

  const sortedEvents = [...events].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  return (
    <Box sx={{ maxWidth: 400 }}>
      <Stepper orientation="vertical">
        {sortedEvents.map((event) => (
          <Step key={event.id} active={true} expanded={true}>
            <StepLabel
              icon={getStepIcon(event.type)}
              sx={{ '& .MuiStepLabel-label': { fontWeight: 900, color: 'white' } }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                <Typography variant="body2" fontWeight={800}>{event.type.replace('_', ' ')}</Typography>
                <Typography variant="caption" color="textSecondary" sx={{ fontFamily: 'JetBrains Mono' }}>
                  {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Typography>
              </Box>
            </StepLabel>
            <StepContent>
              <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 1, fontWeight: 500 }}>
                {event.message || `Signal state transitioned to ${event.type}.`}
              </Typography>
              {event.price && (
                <Chip
                  label={`Price: ₹${event.price.toLocaleString()}`}
                  size="small"
                  sx={{ height: 18, fontSize: '0.6rem', fontWeight: 900, bgcolor: 'rgba(255,255,255,0.03)' }}
                />
              )}
            </StepContent>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 1, border: '1px dashed #10b981' }}>
         <Typography variant="caption" sx={{ fontWeight: 800, color: 'primary.main', display: 'block', textAlign: 'center' }}>
           CURRENT STATE: {currentStatus.replace('_', ' ')}
         </Typography>
      </Box>
    </Box>
  );
}
