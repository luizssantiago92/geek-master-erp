import { useEffect, useState } from 'react';

export function useTelegram() {
  const [webApp, setWebApp] = useState(null);

  useEffect(() => {
    if (window.Telegram && window.Telegram.WebApp) {
      const app = window.Telegram.WebApp;
      app.ready();
      setWebApp(app);
    }
  }, []);

  return {
    webApp,
    user: webApp?.initDataUnsafe?.user,
    isTelegram: !!webApp?.initDataUnsafe?.user || !!window.Telegram?.WebApp?.initData,
    onClose: () => webApp?.close(),
  };
}
