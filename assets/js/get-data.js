// find i way to read the base url

const getData = () => {
  fetch('http://india-states-backend.local/wp-json/wp/v2/posts/')
    .then((response) => response.json())
    .then((json) => console.log(json))
}

getData()
