[日本語 Japanese 日语](./docs/readme_ja.md)  
[英語 English 英语](./docs/readme_en.md)  
[中国語（簡体字) Chinese 中文](./docs/readme_chn.md)  


# Other-Discussion
LM Studioでも使えるようにしまた。

```
pip install -r requirements.txt
```

## 引数
|名前|型|説明|
|:--|:--:|--:|
|member|list|議論者の名前|
|member_response|list|1ターンに格納する議論者の発言|
|useMember|int|使用する仲間のメンバー  ただしmemberリストの中にある要素数以上指定は  できない(リミッターをかけている)|
|turn|int|同じメンバーで何回,議論を回すのか|
