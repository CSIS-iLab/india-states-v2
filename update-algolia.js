import algoliasearch from 'algoliasearch'

const client = algoliasearch('$app_key', '$api_key')

const index = client.initIndex('india_states')

let response = await fetch('https://indianstates.csis.org/algolia.json')

if ( response?.ok ) {
  let data = response.json()
  console.log('Response was okay, so we proceed to update algolia')
  index.saveObjects(data, { autoGenerateObjectIDIfNotExist: true })
  return true
} else {
  console.log('some error ocurred', response.json())
  return false
}
