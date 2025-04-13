# UI Components Documentation

## Scroll Indicators

This directory contains components for enhancing user experience with visual cues for scrollable content.

### ScrollIndicator Component

The `ScrollIndicator` component adds a floating animated button that indicates when content is scrollable and disappears once the user scrolls down.

#### Usage

```jsx
import React, { useRef } from 'react';
import { Box } from '@mui/material';
import { ScrollIndicator } from '../components';

const MyComponent = () => {
  const scrollableRef = useRef(null);
  
  return (
    <Box 
      ref={scrollableRef}
      sx={{ 
        height: '400px', 
        overflowY: 'auto' 
      }}
    >
      {/* Your long scrollable content here */}
      
      <ScrollIndicator 
        containerRef={scrollableRef}
        position="bottom-right" 
        threshold={100}
        offsetBottom={20}
      />
    </Box>
  );
};
```

#### Props

- `containerRef` (required): React ref to the scrollable container
- `position`: Position of the indicator (options: `'sidebar'`, `'bottom-right'`, `'bottom-center'`)
- `threshold`: Scroll threshold in pixels to show/hide indicator (default: `100`)
- `offsetBottom`: Offset from bottom in pixels (default: `20`)
- `iconStyle`: Additional styles for the icon

### ScrollableContent Component

The `ScrollableContent` component is a wrapper that simplifies adding scroll indicators to content.

#### Usage

```jsx
import React from 'react';
import { ScrollableContent } from '../components';

const MyComponent = () => {
  return (
    <ScrollableContent 
      maxHeight="400px"
      component="paper"
      indicatorPosition="bottom-right"
    >
      {/* Your long content here */}
    </ScrollableContent>
  );
};
```

#### Props

- `children`: Content to be scrollable
- `component`: Component to use as container (`'div'` or `'paper'`)
- `maxHeight`: Maximum height of the container (default: `'70vh'`)
- `indicatorPosition`: Position of scroll indicator (default: `'bottom-right'`)
- `threshold`: Scroll threshold to show/hide indicator (default: `100`)
- `sx`: Additional styles for the container

## PageLayout Component

The `PageLayout` component has built-in support for scroll indicators.

#### Usage

```jsx
import React from 'react';
import { PageLayout } from '../components';

const MyPage = () => {
  return (
    <PageLayout 
      title="My Page Title"
      scrollIndicator={true}
    >
      {/* Your page content here */}
    </PageLayout>
  );
};
```

## Development Utilities

A debugging utility is available to help identify scrollable elements that might benefit from scroll indicators:

```jsx
import { enableScrollDebugger, disableScrollDebugger } from '../utils/scrollIndicatorFinder';

// In development, call this in your browser console:
enableScrollDebugger();

// To disable:
disableScrollDebugger();
```

This will highlight scrollable elements in the application and display their scroll properties. 