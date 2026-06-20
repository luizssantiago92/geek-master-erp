import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [isRegistrationComplete, setIsRegistrationComplete] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedState = localStorage.getItem('isRegistrationComplete');
    if (savedState === 'true') {
      setIsRegistrationComplete(true);
    }
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  const completeRegistration = () => {
    setIsRegistrationComplete(true);
    localStorage.setItem('isRegistrationComplete', 'true');
  };

  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    setIsRegistrationComplete(false);
    localStorage.removeItem('user');
    localStorage.removeItem('isRegistrationComplete');
  };

  const updateUser = (data) => {
    const updatedUser = { ...user, ...data };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  return (
    <UserContext.Provider value={{ user, isRegistrationComplete, completeRegistration, login, logout, updateUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
