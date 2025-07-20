// Utility to generate and manage user session ID
export function getUserSessionId(): string {
  // Check if we're on the client side
  if (typeof window === 'undefined') {
    return 'server_session';
  }

  // Try to get existing session ID from localStorage
  let sessionId = localStorage.getItem('user_session_id');
  
  if (!sessionId) {
    // Generate a new session ID if one doesn't exist
    sessionId = 'user_' + Math.random().toString(36).substring(2, 15) + 
                Math.random().toString(36).substring(2, 15);
    localStorage.setItem('user_session_id', sessionId);
  }
  
  return sessionId;
}

// Function to clear session (for logout)
export function clearUserSession(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('user_session_id');
  }
}
