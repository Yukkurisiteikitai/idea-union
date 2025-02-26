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
