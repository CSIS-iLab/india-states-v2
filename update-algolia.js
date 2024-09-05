import algoliasearch from 'algoliasearch'

const client = algoliasearch(`$app_key`, `$api_key`)

const index = client.initIndex('india_states')

fetch('https://indianstates.csis.org/algolia.json')
  .then((response) => response.json())
  .then((data) =>
    index.saveObjects(data, { autoGenerateObjectIDIfNotExist: true })
  )
  .catch ( e => {
    console.error(e)
    console.error(e.message)
  })
