const MosaicDivider = () => {
  return (
    <div className="flex items-center gap-2 py-2">
      <div className="flex-1 h-px bg-border" />
      <div className="flex items-center gap-1.5">
        <div className="w-2 h-2 rotate-45 bg-terracotta/60" />
        <div className="w-2 h-2 rotate-45 bg-ceramic/60" />
        <div className="w-2 h-2 rotate-45 bg-gold/60" />
        <div className="w-2 h-2 rotate-45 bg-ceramic/60" />
        <div className="w-2 h-2 rotate-45 bg-terracotta/60" />
      </div>
      <div className="flex-1 h-px bg-border" />
    </div>
  );
};

export default MosaicDivider;
