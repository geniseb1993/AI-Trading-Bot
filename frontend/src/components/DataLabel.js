import React from 'react';
import { Chip, Tooltip, Box } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import PropTypes from 'prop-types';

/**
 * DataLabel component for displaying data source information
 */
const DataLabel = ({ type }) => {
  let color = 'default';
  let label = 'Unknown';

  switch (type) {
    case 'mock':
      color = 'secondary';
      label = 'Mock Data';
      break;
    case 'real':
      color = 'success';
      label = 'Real Data';
      break;
    case 'ai':
      color = 'primary';
      label = 'AI Generated';
      break;
    case 'synthetic':
      color = 'warning';
      label = 'Synthetic';
      break;
    default:
      color = 'default';
      label = 'Unknown';
  }

  return (
    <Chip
      size="small"
      color={color}
      label={label}
      variant="outlined"
      sx={{ fontWeight: 'medium', fontSize: '0.7rem' }}
    />
  );
};

/**
 * Container component that wraps content with a data label
 */
const DataLabelContainer = ({ children, type, tooltip = '', sx = {} }) => {
  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%', ...sx }}>
      <Box
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}
      >
        <Tooltip title={tooltip} arrow placement="left">
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {tooltip && <InfoIcon fontSize="small" sx={{ color: 'text.secondary', mr: 0.5 }} />}
            <DataLabel type={type} />
          </Box>
        </Tooltip>
      </Box>
      {children}
    </Box>
  );
};

DataLabel.propTypes = {
  type: PropTypes.oneOf(['mock', 'real', 'ai', 'synthetic', 'unknown']).isRequired
};

DataLabelContainer.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.oneOf(['mock', 'real', 'ai', 'synthetic', 'unknown']).isRequired,
  tooltip: PropTypes.string,
  sx: PropTypes.object
};

export default DataLabel;
export { DataLabelContainer }; 