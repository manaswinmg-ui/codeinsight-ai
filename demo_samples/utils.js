// Issue 5: Unused import (will trigger ESLint warning)
import { format } from 'date-fns';

function processConfig(configStr) {
  // Issue 6: Dangerous eval() usage (Security Vulnerability)
  let config = eval(configStr);
  
  // Issue 7: Unused local variable (will trigger ESLint warning)
  let unusedVar = 42;
  
  return config;
}

export { processConfig };
