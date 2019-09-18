export default function createPromiseToken(cbPromise) {
  const token = {
    cancelled: false,
    cancel: (callback) => {
      token.cancelled = true;

      if (callback) {
        callback();
      }
    },
  };


  const request = new Promise((resolve, reject) => {
    cbPromise
      .then((data) => {
        if (!token.cancelled) {
          resolve(data);
        }
      })
      .catch(reject);
  });


  return { token, request };
}
