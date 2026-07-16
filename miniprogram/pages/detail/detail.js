const api = require('../../utils/api')
const app = getApp()

const TYPE_COLORS = {
  physical_constraint: '#5B8FF9', concept: '#5AD8A6',
  definitional_axiom: '#F6BD16', theorem: '#9270CA',
  bridging_proposition: '#5D9CEC', deduction: '#F08080',
  composite_deduction: '#E8684A'
}
const TYPE_LABELS = {
  physical_constraint: '物理约束', concept: '概念',
  definitional_axiom: '公理', theorem: '定理',
  bridging_proposition: '桥接命题', deduction: '推论',
  composite_deduction: '复合推论'
}

Page({
  data: {
    node: null,
    upstream: [],
    downstream: [],
    articles: [],
    stmtExpanded: false
  },

  onLoad(options) {
    if (!app.globalData.loaded) {
      // Wait for data
      setTimeout(() => this.loadNode(options.id), 500)
    } else {
      this.loadNode(options.id)
    }
  },

  loadNode(id) {
    const nodeMap = api.getNodeMap()
    const n = nodeMap[id]
    if (!n) {
      wx.showToast({ title: '未找到', icon: 'none' })
      return
    }

    const upstream = api.getUpstream(id).map(e => this._formatDep(e, 'up'))
    const downstream = api.getDownstream(id).map(e => this._formatDep(e, 'down'))
    const articles = api.getArticles(id)

    const created = n.created || ''
    const revised = n.revised || ''
    let dateInfo = ''
    if (created) {
      dateInfo = `创建于 ${created}`
      if (revised && revised !== created) dateInfo += ` · 修订于 ${revised}`
    }

    this.setData({
      node: {
        ...n,
        dotColor: TYPE_COLORS[n.type] || '#999',
        typeLabel: TYPE_LABELS[n.type] || n.type,
        layerLabel: app.globalData.layerLabels[n.layer] || n.layer,
        summary: n['人话摘要'] || '',
        dateInfo
      },
      upstream,
      downstream,
      articles,
      stmtExpanded: false
    })
  },

  _formatDep(e, dir) {
    const nodeMap = api.getNodeMap()
    const n = nodeMap[dir === 'up' ? e.target : e.source]
    if (!n) return { id: dir === 'up' ? e.target : e.source, term_zh: '?', dotColor: '#999', typeLabel: '', relation: e.relation_label || e.relation }
    return {
      id: n.id,
      term_zh: n.term_zh || n.term,
      term: n.term,
      dotColor: TYPE_COLORS[n.type] || '#999',
      typeLabel: TYPE_LABELS[n.type] || n.type,
      relation: e.relation_label || e.relation,
      excerpt: (n['人话摘要'] || '').slice(0, 50)
    }
  },

  toggleStmt() {
    this.setData({ stmtExpanded: !this.data.stmtExpanded })
  },

  goNode(e) {
    const id = e.currentTarget.dataset.id
    if (!id) return
    wx.redirectTo({ url: `/pages/detail/detail?id=${id}` })
  }
})
