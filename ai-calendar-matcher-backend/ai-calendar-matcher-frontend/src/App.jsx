import React, { useState } from "react";

import LandingPage from "./components/LandingPage";
import HomePage  from "./components/HomePage";

function App() {
  const [user, setUser] = useState(null);

  if (!user) {
    return <LandingPage onLogin={setUser} />;
  }

    return (
        <div>
        <HomePage />
        <button onClick={() => setUser(null)}>Logout</button>
      </div>
 
  );
}

export default App;
