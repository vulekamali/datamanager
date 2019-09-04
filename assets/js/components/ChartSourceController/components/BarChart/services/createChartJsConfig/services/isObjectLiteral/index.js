const isObjectLiteral = (value) => {
  return (
    value !== null
    && typeof value === 'object'
    && !Array.isArray(value)
  );
};

export default isObjectLiteral;
