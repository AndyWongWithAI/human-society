const API = 'https://human-society.intelab.cn'

let data = null
let nodeMap = {}
let upstreamMap = {}
let downstreamMap = {}
let articleMap = {}

function loadData() {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API + '/graph-data.json',
      success: res => {
        if (res.statusCode === 200) {
          data = res.data
          nodeMap = {}
          upstreamMap = {}
          downstreamMap = {}
          articleMap = data.entity_articles || {}
          data.nodes.forEach(n => {
            nodeMap[n.id] = n
            upstreamMap[n.id] = []
            downstreamMap[n.id] = []
          })
          data.edges.forEach(e => {
            if (upstreamMap[e.source]) upstreamMap[e.source].push(e)
            if (downstreamMap[e.target]) downstreamMap[e.target].push(e)
          })
          resolve(data)
        } else {
          reject(new Error('API error ' + res.statusCode))
        }
      },
      fail: reject
    })
  })
}

module.exports = {
  API,
  loadData,
  getData() { return data },
  getNodeMap() { return nodeMap },
  getUpstream(id) { return upstreamMap[id] || [] },
  getDownstream(id) { return downstreamMap[id] || [] },
  getArticles(id) { return articleMap[id] || [] }
}
