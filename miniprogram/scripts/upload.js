#!/usr/bin/env node
/**
 * 上传小程序代码 → 微信后台
 * 上传后到 mp.weixin.qq.com 提交审核即可发布
 */
const ci = require('miniprogram-ci')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
const pkg = require('../package.json')

async function main() {
  // 先验证
  try {
    require('child_process').execSync(`node "${path.join(__dirname, 'validate.js')}"`, {
      cwd: ROOT, stdio: 'inherit'
    })
  } catch (e) {
    console.error('验证未通过，终止上传')
    process.exit(1)
  }

  const project = new ci.Project({
    appid: 'wx167514146b03982c',
    type: 'miniProgram',
    projectPath: ROOT,
    privateKeyPath: path.join(ROOT, 'private.key'),
    ignores: ['node_modules/**/*', 'scripts/**/*', 'private.key', 'package*.json', '.gitignore', 'preview-qrcode.png']
  })

  const version = pkg.version || '1.0.0'
  const desc = process.argv[2] || '更新'

  console.log(`📤 上传版本 ${version}: ${desc}`)
  try {
    const result = await ci.upload({
      project,
      version,
      desc,
      setting: { es6: true, minify: true, urlCheck: true },
      onProgressUpdate: (info) => {
        if (info && info.status) console.log('  ' + info.status)
      }
    })
    console.log('✅ 上传成功！')
    console.log('下一步: 登录 mp.weixin.qq.com → 版本管理 → 提交审核')
  } catch (e) {
    console.error('❌ 上传失败: ' + (e.message || e))
    process.exit(1)
  }
}

main()
