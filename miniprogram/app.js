const api = require('./utils/api')

App({
  globalData: {
    nodes: [],
    edges: [],
    loaded: false,
    loadError: false,
    colors: {
      physical_constraint: '#5B8FF9',
      concept: '#5AD8A6',
      definitional_axiom: '#F6BD16',
      theorem: '#9270CA',
      bridging_proposition: '#5D9CEC',
      deduction: '#F08080',
      composite_deduction: '#E8684A'
    },
    typeLabels: {
      physical_constraint: '物理约束',
      concept: '概念',
      definitional_axiom: '公理',
      theorem: '定理',
      bridging_proposition: '桥接命题',
      deduction: '推论',
      composite_deduction: '复合推论'
    },
    layerLabels: { L0: '物理约束', L1: '定义', L2: '桥接', L3: '推论', L4: '复合' },
    layerOrder: ['L0', 'L1', 'L2', 'L3', 'L4']
  },

  onLaunch() {
    api.loadData().then(data => {
      this.globalData.nodes = data.nodes
      this.globalData.edges = data.edges
      this.globalData.loaded = true
    }).catch(err => {
      console.error('Data load failed:', err)
      this.globalData.loadError = true
    })
  }
})
