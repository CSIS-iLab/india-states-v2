import algoliasearch from 'algoliasearch'

const client = algoliasearch('$app_key', '$api_key')

const index = client.initIndex('india_states')

await fetch('https://indian-states-v2.netlify.app/algolia.json')
  .then((response) => response.json())
  // .then( data => console.log(data))
  .then((data) =>
    index.saveObjects(data, { autoGenerateObjectIDIfNotExist: true })
  )
