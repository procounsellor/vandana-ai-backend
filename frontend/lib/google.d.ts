interface Window {
  google?: {
    accounts: {
      id: {
        initialize: (config: { client_id: string; callback: (res: { credential: string }) => void }) => void;
        prompt: () => void;
      };
    };
  };
}
