let response;
        try {
          response = await fetch('http://localhost:8000/health', { 
            method: 'GET',
            signal: controller.signal,
            cache: 'no-cache',
            mode: 'cors'
          });
        } catch (healthErr) {
          // If health endpoint fails, try root endpoint as fallback
          try {
            response = await fetch('http://localhost:8000/', { 
              method: 'GET',
              signal: controller.signal,
              cache: 'no-cache',
              mode: 'cors'
            });
          } catch (rootErr) {
            throw healthErr; // Throw original error
          }
        }
=======
        // Try health endpoint first, fallback to root if needed
        let response;
        try {
          response = await fetch('/api/health', {
            method: 'GET',
            signal: controller.signal,
            cache: 'no-cache',
            mode: 'cors'
          });
        } catch (healthErr) {
          // If health endpoint fails, try root endpoint as fallback
          try {
            response = await fetch('/', {
              method: 'GET',
              signal: controller.signal,
              cache: 'no-cache',
              mode: 'cors'
            });
          } catch (rootErr) {
            throw healthErr; // Throw original error
          }
        }
