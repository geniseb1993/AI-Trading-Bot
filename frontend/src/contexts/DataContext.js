import React, { createContext, useContext, useState, useCallback, useReducer, useMemo } from 'react';

// Define the initial state structure
const initialState = {
  institutionalFlow: {
    data: {},
    loading: false,
    error: null,
    isStale: true,
    lastFetched: null
  },
  marketData: {
    data: {},
    loading: false,
    error: null,
    isStale: true,
    lastFetched: null
  },
  brokerIntegration: {
    data: {},
    loading: false,
    error: null,
    isStale: true,
    lastFetched: null
  },
  riskManagement: {
    data: {},
    loading: false,
    error: null,
    isStale: true,
    lastFetched: null
  },
  apiConfiguration: {
    data: {},
    loading: false,
    error: null,
    isStale: true,
    lastFetched: null
  }
};

// Create a reducer to handle different data domains
const dataReducer = (state, action) => {
  const { type, payload, domain } = action;
  
  switch (type) {
    case 'FETCH_START':
      return {
        ...state,
        [domain]: {
          ...state[domain],
          loading: true,
          error: null
        }
      };
    case 'FETCH_SUCCESS':
      return {
        ...state,
        [domain]: {
          ...state[domain],
          data: payload,
          loading: false,
          error: null,
          isStale: false,
          lastFetched: new Date().toISOString()
        }
      };
    case 'FETCH_ERROR':
      return {
        ...state,
        [domain]: {
          ...state[domain],
          loading: false,
          error: payload,
          isStale: true
        }
      };
    case 'SET_STALE':
      return {
        ...state,
        [domain]: {
          ...state[domain],
          isStale: true
        }
      };
    case 'CLEAR_DOMAIN':
      return {
        ...state,
        [domain]: {
          ...initialState[domain]
        }
      };
    case 'RESET_ALL':
      return initialState;
    default:
      return state;
  }
};

// Create context
const DataContext = createContext();

// Provider component
export const DataProvider = ({ children }) => {
  const [state, dispatch] = useReducer(dataReducer, initialState);
  
  // Create domain-specific data access functions
  const getInstitutionalFlowData = useCallback((forceRefresh = false) => {
    const domain = 'institutionalFlow';
    const domainData = state[domain];
    
    // Check if data needs to be refreshed
    if (forceRefresh || domainData.isStale || !domainData.lastFetched) {
      dispatch({ type: 'SET_STALE', domain });
    }
    
    return domainData;
  }, [state]);
  
  const getRiskManagementData = useCallback((forceRefresh = false) => {
    const domain = 'riskManagement';
    const domainData = state[domain];
    
    if (forceRefresh || domainData.isStale || !domainData.lastFetched) {
      dispatch({ type: 'SET_STALE', domain });
    }
    
    return domainData;
  }, [state]);
  
  const getMarketData = useCallback((forceRefresh = false) => {
    const domain = 'marketData';
    const domainData = state[domain];
    
    if (forceRefresh || domainData.isStale || !domainData.lastFetched) {
      dispatch({ type: 'SET_STALE', domain });
    }
    
    return domainData;
  }, [state]);
  
  const getApiConfigurationData = useCallback((forceRefresh = false) => {
    const domain = 'apiConfiguration';
    const domainData = state[domain];
    
    if (forceRefresh || domainData.isStale || !domainData.lastFetched) {
      dispatch({ type: 'SET_STALE', domain });
    }
    
    return domainData;
  }, [state]);
  
  // Create update functions for each domain
  const updateInstitutionalFlowData = useCallback((data) => {
    dispatch({
      type: 'FETCH_SUCCESS',
      domain: 'institutionalFlow',
      payload: data
    });
  }, []);
  
  const updateRiskManagementData = useCallback((data) => {
    dispatch({
      type: 'FETCH_SUCCESS',
      domain: 'riskManagement',
      payload: data
    });
  }, []);
  
  const updateMarketData = useCallback((data) => {
    dispatch({
      type: 'FETCH_SUCCESS',
      domain: 'marketData',
      payload: data
    });
  }, []);
  
  const updateApiConfigurationData = useCallback((data) => {
    dispatch({
      type: 'FETCH_SUCCESS',
      domain: 'apiConfiguration',
      payload: data
    });
  }, []);
  
  // Create loading state setters
  const setLoading = useCallback((domain, isLoading = true) => {
    dispatch({
      type: isLoading ? 'FETCH_START' : 'FETCH_SUCCESS',
      domain,
      payload: isLoading ? null : state[domain].data
    });
  }, [state]);
  
  // Create error state setters
  const setError = useCallback((domain, error) => {
    dispatch({
      type: 'FETCH_ERROR',
      domain,
      payload: error
    });
  }, []);
  
  // Clear a specific domain's data
  const clearDomainData = useCallback((domain) => {
    dispatch({
      type: 'CLEAR_DOMAIN',
      domain
    });
  }, []);
  
  // Reset all data
  const resetAllData = useCallback(() => {
    dispatch({ type: 'RESET_ALL' });
  }, []);
  
  // Memoize the context value to prevent unnecessary renders
  const contextValue = useMemo(() => ({
    state,
    getInstitutionalFlowData,
    getRiskManagementData,
    getMarketData,
    getApiConfigurationData,
    updateInstitutionalFlowData,
    updateRiskManagementData,
    updateMarketData,
    updateApiConfigurationData,
    setLoading,
    setError,
    clearDomainData,
    resetAllData
  }), [
    state, 
    getInstitutionalFlowData,
    getRiskManagementData,
    getMarketData,
    getApiConfigurationData,
    updateInstitutionalFlowData,
    updateRiskManagementData,
    updateMarketData,
    updateApiConfigurationData,
    setLoading,
    setError,
    clearDomainData,
    resetAllData
  ]);
  
  return (
    <DataContext.Provider value={contextValue}>
      {children}
    </DataContext.Provider>
  );
};

// Create a custom hook for using the data context
export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

// Create domain-specific hooks to limit access and ensure isolation
export const useInstitutionalFlowData = () => {
  const { 
    state, 
    getInstitutionalFlowData, 
    updateInstitutionalFlowData,
    setLoading,
    setError
  } = useData();
  
  return {
    data: state.institutionalFlow.data,
    loading: state.institutionalFlow.loading,
    error: state.institutionalFlow.error,
    isStale: state.institutionalFlow.isStale,
    lastFetched: state.institutionalFlow.lastFetched,
    getData: getInstitutionalFlowData,
    updateData: updateInstitutionalFlowData,
    setLoading: (isLoading) => setLoading('institutionalFlow', isLoading),
    setError: (error) => setError('institutionalFlow', error)
  };
};

export const useRiskManagementData = () => {
  const { 
    state, 
    getRiskManagementData, 
    updateRiskManagementData,
    setLoading,
    setError
  } = useData();
  
  return {
    data: state.riskManagement.data,
    loading: state.riskManagement.loading,
    error: state.riskManagement.error,
    isStale: state.riskManagement.isStale,
    lastFetched: state.riskManagement.lastFetched,
    getData: getRiskManagementData,
    updateData: updateRiskManagementData,
    setLoading: (isLoading) => setLoading('riskManagement', isLoading),
    setError: (error) => setError('riskManagement', error)
  };
};

export const useMarketData = () => {
  const { 
    state, 
    getMarketData, 
    updateMarketData,
    setLoading,
    setError
  } = useData();
  
  return {
    data: state.marketData.data,
    loading: state.marketData.loading,
    error: state.marketData.error,
    isStale: state.marketData.isStale,
    lastFetched: state.marketData.lastFetched,
    getData: getMarketData,
    updateData: updateMarketData,
    setLoading: (isLoading) => setLoading('marketData', isLoading),
    setError: (error) => setError('marketData', error)
  };
};

export const useApiConfigurationData = () => {
  const { 
    state, 
    getApiConfigurationData, 
    updateApiConfigurationData,
    setLoading,
    setError
  } = useData();
  
  return {
    data: state.apiConfiguration.data,
    loading: state.apiConfiguration.loading,
    error: state.apiConfiguration.error,
    isStale: state.apiConfiguration.isStale,
    lastFetched: state.apiConfiguration.lastFetched,
    getData: getApiConfigurationData,
    updateData: updateApiConfigurationData,
    setLoading: (isLoading) => setLoading('apiConfiguration', isLoading),
    setError: (error) => setError('apiConfiguration', error)
  };
}; 