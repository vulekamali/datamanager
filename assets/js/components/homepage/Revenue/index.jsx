import ValueBlocks from './../ValueBlocks/index.jsx';


export default function Revenue({ values }) {
  const items = values.data.reduce(
    (result, val) => {
      return {
        ...result,
        [val.category]: {
          value: val.amount,
        },
      };
    },
    {},
  );

  return (
    <ValueBlocks
      {...{ items }}
    />
  );
}
