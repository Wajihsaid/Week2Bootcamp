import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";

const TUNISIAN_LANDMARKS = [
  {
    name: "Sidi Bou Said",
    era: "Blue & White Village",
    title: "Coastal Paradise",
    emoji: "🏠",
    gradient: "from-blue-500/20 via-sky-400/20 to-cyan-300/20",
    ringColor: "border-blue-500/40",
  },
  {
    name: "Carthage Ruins",
    era: "Ancient Wonder",
    title: "Archaeological Marvel",
    emoji: "🏛️",
    gradient: "from-amber-500/20 via-orange-400/20 to-yellow-500/20",
    ringColor: "border-amber-500/40",
  },
  {
    name: "El Jem Amphitheatre",
    era: "Roman Legacy",
    title: "Colosseum of Africa",
    emoji: "🏟️",
    gradient: "from-orange-500/20 via-red-500/20 to-pink-500/20",
    ringColor: "border-orange-500/40",
  },
  {
    name: "Sahara Desert",
    era: "Golden Dunes",
    title: "Endless Beauty",
    emoji: "🏜️",
    gradient: "from-yellow-500/20 via-amber-500/20 to-orange-400/20",
    ringColor: "border-yellow-500/40",
  },
  {
    name: "Zitouna Mosque",
    era: "Heart of Medina",
    title: "Spiritual Center",
    emoji: "🕌",
    gradient: "from-emerald-500/20 via-green-500/20 to-teal-500/20",
    ringColor: "border-emerald-500/40",
  },
  {
    name: "Tunisian Olive Oil",
    era: "Liquid Gold",
    title: "World-Renowned",
    emoji: "🫒",
    gradient: "from-lime-500/20 via-green-600/20 to-emerald-500/20",
    ringColor: "border-lime-500/40",
  },
  {
    name: "Tunisian Café",
    era: "Social Hub",
    title: "Coffee Culture",
    emoji: "☕",
    gradient: "from-amber-600/20 via-brown-500/20 to-orange-600/20",
    ringColor: "border-amber-600/40",
  },
  {
    name: "Hand of Fatima",
    era: "Cultural Symbol",
    title: "Protection & Blessing",
    emoji: "🧿",
    gradient: "from-indigo-500/20 via-blue-500/20 to-purple-500/20",
    ringColor: "border-indigo-500/40",
  },
];

const TunisianShowcase = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % TUNISIAN_LANDMARKS.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const current = TUNISIAN_LANDMARKS[currentIndex];

  return (
    <div className="w-full max-w-sm mx-auto">
      {/* Premium 3D Card */}
      <motion.div
        className="relative"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, rotateY: -90, scale: 0.8 }}
            animate={{ opacity: 1, rotateY: 0, scale: 1 }}
            exit={{ opacity: 0, rotateY: 90, scale: 0.8 }}
            transition={{ duration: 0.6, type: "spring", stiffness: 100 }}
            className="relative"
          >
            {/* Glass morphism card */}
            <div className={`relative bg-gradient-to-br ${current.gradient} backdrop-blur-xl rounded-3xl border-2 ${current.ringColor} shadow-2xl overflow-hidden`}>
              {/* Animated gradient overlay */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-tr from-white/5 via-transparent to-white/10"
                animate={{
                  backgroundPosition: ["0% 0%", "100% 100%"],
                }}
                transition={{
                  duration: 8,
                  repeat: Infinity,
                  repeatType: "reverse",
                }}
              />

              {/* Content */}
              <div className="relative p-8 flex flex-col items-center text-center">
                {/* Floating emoji with glow */}
                <motion.div
                  className="relative mb-6"
                  animate={{
                    y: [0, -10, 0],
                    rotate: [0, 5, -5, 0],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
                  {/* Glow effect */}
                  <div className="absolute inset-0 blur-2xl opacity-50">
                    <div className="text-8xl">{current.emoji}</div>
                  </div>
                  {/* Main emoji */}
                  <div className="relative text-8xl filter drop-shadow-2xl">
                    {current.emoji}
                  </div>
                </motion.div>

                {/* Name & Title */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="space-y-2"
                >
                  <h3 className="font-display text-2xl font-bold text-foreground leading-tight">
                    {current.name}
                  </h3>
                  <div className="inline-block px-4 py-1.5 bg-background/60 rounded-full backdrop-blur-sm border border-border/50">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      {current.title}
                    </p>
                  </div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {current.era}
                  </p>
                </motion.div>

                {/* Decorative corner elements */}
                <div className="absolute top-3 left-3 w-6 h-6 border-l-2 border-t-2 border-current opacity-30 rounded-tl-lg" />
                <div className="absolute top-3 right-3 w-6 h-6 border-r-2 border-t-2 border-current opacity-30 rounded-tr-lg" />
                <div className="absolute bottom-3 left-3 w-6 h-6 border-l-2 border-b-2 border-current opacity-30 rounded-bl-lg" />
                <div className="absolute bottom-3 right-3 w-6 h-6 border-r-2 border-b-2 border-current opacity-30 rounded-br-lg" />
              </div>

              {/* Floating particles */}
              {[...Array(6)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-1 h-1 rounded-full bg-gold/60"
                  style={{
                    top: `${10 + Math.random() * 80}%`,
                    left: `${10 + Math.random() * 80}%`,
                  }}
                  animate={{
                    y: [0, -20, 0],
                    opacity: [0.3, 1, 0.3],
                    scale: [1, 1.5, 1],
                  }}
                  transition={{
                    duration: 3 + i * 0.5,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: i * 0.3,
                  }}
                />
              ))}
            </div>

            {/* 3D shadow effect */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/5 rounded-3xl transform translate-y-1 -z-10" />
          </motion.div>
        </AnimatePresence>

        {/* Navigation dots */}
        <div className="flex items-center justify-center gap-2 mt-6">
          {TUNISIAN_LANDMARKS.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentIndex(i)}
              className="group relative"
            >
              <motion.div
                className={`rounded-full transition-all duration-300 ${i === currentIndex
                    ? "bg-primary w-8 h-2.5"
                    : "bg-sand w-2.5 h-2.5 group-hover:bg-sand-light"
                  }`}
                layoutId={i === currentIndex ? "active-dot" : undefined}
              />
            </button>
          ))}
        </div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="text-center mt-6 text-xs text-muted-foreground font-body tracking-wide"
        >
          Click to explore • Auto-cycling every 4s
        </motion.p>
      </motion.div>
    </div>
  );
};

export default TunisianShowcase;