import { useState } from "react";

const CHARACTERS = [
  { id: "hannibal", name: "Hannibal Barca", era: "Ancient Carthage", emoji: "⚔️" },
  { id: "dido", name: "Queen Dido", era: "Founding of Carthage", emoji: "👑" },
  { id: "ibn-khaldun", name: "Ibn Khaldun", era: "14th Century", emoji: "📜" },
  { id: "bourguiba", name: "Habib Bourguiba", era: "Modern Tunisia", emoji: "🏛️" },
  { id: "kahena", name: "Al-Kahina", era: "7th Century", emoji: "🛡️" },
];

interface CharacterAvatarProps {
  activeCharacter: string | null;
  isSpeaking: boolean;
}

const CharacterAvatar = ({ activeCharacter, isSpeaking }: CharacterAvatarProps) => {
  const character = CHARACTERS.find((c) => c.id === activeCharacter) || CHARACTERS[0];

  return (
    <div className="flex flex-col items-center gap-4">
      <div
        className={`relative w-32 h-32 rounded-full bg-card border-4 border-sand flex items-center justify-center transition-all duration-500 ${
          isSpeaking ? "speaking-glow scale-105" : ""
        }`}
      >
        <span className="text-5xl">{character.emoji}</span>
        {isSpeaking && (
          <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 flex items-end gap-0.5 h-4">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="w-1 bg-ceramic rounded-full voice-wave-bar"
                style={{
                  height: "16px",
                  animationDelay: `${i * 0.15}s`,
                }}
              />
            ))}
          </div>
        )}
      </div>
      <div className="text-center">
        <h3 className="font-display text-lg font-semibold text-foreground">{character.name}</h3>
        <p className="text-sm text-muted-foreground">{character.era}</p>
      </div>
    </div>
  );
};

export { CharacterAvatar, CHARACTERS };
