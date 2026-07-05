function Container({ children }) {
  return (
    <div className="max-w-[1400px] mx-auto px-6 md:px-10 lg:px-16 xl:px-24 2xl:px-32">
      {children}
    </div>
  );
}

export default Container;