export default function fetchWrapper(url) {
  return new Promise((resolve, reject) => {
    fetch(url)
      .then((response) => {
        if (!response.ok) {
          reject(response);
        }

        response.json()
          .then((data) => {
            if (data.success === 'false') {
              reject('Requested failed inside CKAN');
            }

            resolve(data);
          })
          .catch(reject);
      })
      .catch(reject);
  });
}
