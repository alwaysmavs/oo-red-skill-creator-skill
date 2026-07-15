# Chinese Listing Copy

Generate copy-ready Xiaohongshu fields after the Skill is complete. Base the
copy on the actual runtime contract rather than authoring intentions.

## Skill 名称

- Use a clear Chinese outcome or product phrase.
- Keep it within 15 characters.
- Avoid exposing an internal package name unless it is already a recognizable
  brand.

## Skill ID

- Prefer the normalized internal Skill name.
- Use lowercase letters, digits, and hyphens.
- Do not change an ID the user already reserved unless it is invalid.

## 简介

Write one compact Chinese paragraph that covers:

1. the primary user outcome;
2. the main inputs or use cases;
3. the distinguishing result or reliability feature.

Do not lead with installation instructions. Do not claim that an optional
runtime is required.

## Skill 介绍

Write concise Chinese Markdown with only useful sections:

```markdown
# <中文名称>

<一句价值主张>

## 可以做什么
- <主要场景>

## 怎么使用
<输入和示例请求>

## 运行方式
<standard、OO-required 或 dual-runtime 的真实说明>

## 注意事项
<费用、等待、精度、隐私或输出边界>
```

Keep implementation details subordinate to the Skill's domain value. For a
dual-runtime Skill, explain that it selects an available path without dumping
connector commands into the listing.

## Version and suggestions

- Use the established version when present; otherwise recommend `1.0.0` for a
  stable first public release.
- Suggest a category and 3–6 Chinese tags when helpful.
- State whether the source is original, adapted with attribution, or reposted;
  do not infer ownership when evidence is missing.

Return the fields in a copyable block and also save them outside the upload ZIP
when producing artifacts.
