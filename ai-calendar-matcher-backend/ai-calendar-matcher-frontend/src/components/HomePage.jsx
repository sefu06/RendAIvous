import React, { useState } from "react";
import "./HomePage.css";

export default function HomePage() {
  const [friends, setFriends] = useState([
    { id: 1, name: "Selina", lastHangout: "Yesterday", initial: "S", email: "selina@example.com" },
    { id: 2, name: "Cindy", lastHangout: "Yesterday", initial: "C", email: "cindy@example.com" },
  ]);

  const [showAddFriend, setShowAddFriend] = useState(false);
  const [newFriendEmail, setNewFriendEmail] = useState("");

  const handleAddFriend = () => {
    if (!newFriendEmail) return;
    const name = newFriendEmail.split("@")[0];
    const newFriend = {
      id: friends.length + 1,
      name: name.charAt(0).toUpperCase() + name.slice(1),
      lastHangout: "Never",
      initial: name.charAt(0).toUpperCase(),
      email: newFriendEmail,
    };
    setFriends([...friends, newFriend]);
    setNewFriendEmail("");
    setShowAddFriend(false);
    alert("Request sent!");
  };

  return (
    <div className="hangouthub-container">
      <div className="app-name">rendAlvous</div>

      <div className="header">
        <h1>Hangout Hub</h1>
        <button
          className="btn-plan"
          onClick={() => setShowAddFriend(true)}
        >
          ✨ Add Friend
        </button>
      </div>

      <div className="dashboard-wrapper">
        <div className="dashboard">
          {/* Left column */}
          <div className="dashboard-left">
            {/* Friends Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <span>👥</span> Friends
                </div>
              </div>

              {/* Add Friend Popup */}
              {showAddFriend && (
                <div className="popup-overlay">
                  <div className="popup">
                    <h3>Add a new friend</h3>
                    <input
                      type="email"
                      placeholder="Enter friend's email"
                      value={newFriendEmail}
                      onChange={(e) => setNewFriendEmail(e.target.value)}
                      className="popup-input"
                    />
                    <div className="popup-buttons">
                      <button onClick={handleAddFriend} className="btn-confirm">
                        Add
                      </button>
                      <button onClick={() => setShowAddFriend(false)} className="btn-cancel">
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              <div className="friends-list">
                {friends.map((friend) => (
                  <div key={friend.id} className="friend-item">
                    <div className="avatar">{friend.initial}</div>
                    <div>
                      <h4>{friend.name}</h4>
                      <p>Last hangout: {friend.lastHangout}</p>
                      <p>Email: {friend.email}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Groups Card */}
            <div className="card blue-outline">
              <div className="card-header">
                <div className="card-title">
                  <span>👥</span> Groups
                </div>
                <input type="text" className="search-input" placeholder="🔍 Search" />
              </div>
              <div className="groups-list">
                {[
                  { name: "women in stem 💪", members: ["S", "C", "E"] },
                  { name: "HR Queens", members: ["A", "B", "C"] },
                  { name: "cool ppl", members: ["X", "Y"] },
                ].map((group, index) => (
                  <div className="group-item" key={index}>
                    <div className="group-info">
                      <div className="avatar">{group.name[0]}</div>
                      <div className="group-details">
                        <h4>{group.name}</h4>
                        <p>{group.members.length} members</p>
                      </div>
                    </div>
                    <div className="member-avatars">
                      {group.members.map((member, i) => (
                        <div className="avatar" key={i}>{member}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Hangout History Card */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <span>🕐</span> Hangout History
                </div>
              </div>
              <div className="history-list">
                {[
                  { icon: "🍺", title: "Social at Rain or Shine", date: "Oct. 6, 2025", location: "UBC", group: "women in stem 💪" },
                  { icon: "🎤", title: "Karaoke Night", date: "Sept. 29, 2025", location: "UBC", group: "HR Queens" },
                ].map((history, index) => (
                  <div className="history-item" key={index}>
                    <div className="history-icon">{history.icon}</div>
                    <div className="history-details">
                      <h4>{history.title}</h4>
                      <div className="history-meta">
                        <span>📅 {history.date}</span>
                        <span>📍 {history.location}</span>
                        <span>👥 {history.group}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right column */}
          <div className="dashboard-right">
            {/* Calendar Card */}
            <div className="card calendar-card">
              <div className="calendar-header">October</div>
              <div className="calendar-grid">
                {["S","M","T","W","T","F","S"].map((day, i) => (
                  <div className="calendar-day-name" key={i}>{day}</div>
                ))}
                {Array.from({length: 31}).map((_, i) => (
                  <div className={`calendar-day ${[1,2,3,6,15,17,19,20,26].includes(i+1) ? "has-event" : ""}`} key={i}>
                    {i+1}
                    {[1,2,3,6,15,17,19,20,26].includes(i+1) && <div className="event-dot"></div>}
                  </div>
                ))}
              </div>
            </div>

            {/* AI Assistant Card */}
            <div className="card ai-assistant-card">
              <div className="card-header">
                <div className="card-title">
                  <span>✨</span> AI Assistant
                </div>
              </div>
              <div className="chat-area">Ask me anything!</div>
              <div className="chat-input-container">
                <input type="text" className="chat-input" placeholder="Ask me anything!" />
                <button className="btn-send">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

