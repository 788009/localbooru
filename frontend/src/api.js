import axios from 'axios'

const api = axios.create({
  baseURL: 'http://10.194.0.100:8000/api'
})

export default {
  getConfig() {
    return api.get('/config').then(res => res.data)
  },
  autocomplete(query) {
    return api.get('/search/autocomplete', { params: { q: query } }).then(res => res.data)
  },
  search(data) {
    return api.post('/search', data).then(res => res.data)
  },
  getImageDetail(id) {
    return api.get(`/images/${id}/detail`).then(res => res.data)
  },
  getImageUrl(id) {
    return `http://10.194.0.100:8000/api/images/${id}/file`
  }
}
