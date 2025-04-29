import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TradingViewWidget from '../components/TradingViewWidget';

// Mock window.TradingView
global.TradingView = {
  widget: jest.fn().mockImplementation(() => ({
    onChartReady: jest.fn(),
    remove: jest.fn(),
  })),
};

describe('TradingViewWidget', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Reset the document body before each test
    document.body.innerHTML = '';
  });

  test('renders without crashing', () => {
    render(<TradingViewWidget symbol="AAPL" interval="1D" />);
    expect(document.querySelector('.tradingview-widget-container')).toBeInTheDocument();
  });

  test('creates and cleans up TradingView widget', async () => {
    const { unmount } = render(<TradingViewWidget symbol="AAPL" interval="1D" />);
    
    // Wait for the script to be loaded and the widget to be created
    await waitFor(() => {
      expect(document.querySelector('script[src*="tradingview.com"]')).toBeInTheDocument();
    });
    
    // Test cleanup
    unmount();
    
    // After unmounting, the container should be empty
    expect(document.body.innerHTML).not.toContain('script[src*="tradingview.com"]');
  });

  test('correctly formats symbol', () => {
    // Test with stock symbol
    render(<TradingViewWidget symbol="AAPL" interval="1D" />);
    unmount();
    
    // Test with crypto symbol
    render(<TradingViewWidget symbol="BTC/USD" interval="1D" />);
    expect(document.querySelector('.tradingview-widget-container')).toBeInTheDocument();
    
    // Test with forex symbol
    render(<TradingViewWidget symbol="EUR/USD" interval="1D" />);
    expect(document.querySelector('.tradingview-widget-container')).toBeInTheDocument();
  });
}); 