import React from 'react';
import { Chip, Tooltip, Box } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';

/**
 * DataLabel component displays a colored label to indicate if data is mock or real
 * 
 * @param {Object} props
 * @param {string} props.type - 'mock' or 'real'
 * @param {string} props.tooltip - Optional tooltip text
 * @param {Object} props.sx - Optional sx prop to override styles
 * @returns {JSX.Element}
 */
const DataLabel = ({ type = 'mock', tooltip = '', sx = {} }) => {
  const isMock = type.toLowerCase() === 'mock';
  const defaultTooltip = isMock 
    ? 'This is sample data for demonstration purposes only' 
    : 'This is real data from the connected data source';
  
  const chipColor = isMock ? 'warning' : 'success';
  const label = isMock ? 'Sample Data' : 'Real Data';
  
  return (
    <Tooltip title={tooltip || defaultTooltip}>
      <Chip
        size="small"
        color={chipColor}
        label={label}
        icon={<InfoIcon fontSize="small" />}
        sx={{ 
          height: '22px', 
          fontSize: '0.7rem', 
          fontWeight: 'bold',
          ...sx 
        }}
      />
    </Tooltip>
  );
};

/**
 * Container component that wraps content with a data label in the corner
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - The content to display
 * @param {string} props.type - 'mock' or 'real'
 * @param {string} props.tooltip - Optional tooltip text
 * @param {string} props.position - Position of the label (topRight, topLeft, bottomRight, bottomLeft)
 * @param {Object} props.sx - Optional sx prop to override styles
 * @returns {JSX.Element}
 */
export const DataLabelContainer = ({ 
  children, 
  type = 'mock', 
  tooltip = '', 
  position = 'topRight',
  sx = {} 
}) => {
  // Calculate position styles
  let positionStyles = {};
  switch (position) {
    case 'topLeft':
      positionStyles = { top: 8, left: 8 };
      break;
    case 'bottomRight':
      positionStyles = { bottom: 8, right: 8 };
      break;
    case 'bottomLeft':
      positionStyles = { bottom: 8, left: 8 };
      break;
    case 'topRight':
    default:
      positionStyles = { top: 8, right: 8 };
  }

  return (
    <Box sx={{ position: 'relative', ...sx }}>
      {children}
      <Box sx={{ position: 'absolute', ...positionStyles, zIndex: 10 }}>
        <DataLabel type={type} tooltip={tooltip} />
      </Box>
    </Box>
  );
};

export default DataLabel; 