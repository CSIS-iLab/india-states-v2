import algoliasearch from 'algoliasearch'

const client = algoliasearch('$app_key', '$api_key')

const index = client.initIndex('india_states')

let response = await fetch('https://indian-states-v2.netlify.app/algolia.json')

if ( response?.ok ) {
  let data = response.json()
  // .then( data => console.log(data))
  index.saveObjects(data, { autoGenerateObjectIDIfNotExist: true })
} else {
  console.log('some error ocurred', response.json())
}
