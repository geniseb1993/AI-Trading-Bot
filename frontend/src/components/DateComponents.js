import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider as MuiLocalizationProvider } from '@mui/x-date-pickers';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

// Re-export the components
export const LocalizationProvider = MuiLocalizationProvider;
export { AdapterDateFns, DatePicker }; 