#let data = json(sys.inputs.data_path)
#let white = rgb("#f8fafc")
#let muted = rgb("#b8c5cd")
#let page-bg = gradient.linear(angle: 90deg, rgb("#bdc3c7"), rgb("#2c3e50"))
#let today-bg = gradient.linear(rgb("#6dd5ed"), rgb("#2193b0"))
#let air-bg = gradient.linear(rgb("#348ac7"), rgb("#7474bf"))
#let hours-bg = gradient.linear(rgb("#102833"), rgb("#2c6279"))
#let days-bg = gradient.linear(rgb("#2c5364"), rgb("#0f2027"))
#let temp-line = gradient.linear(rgb("#f18360"), rgb("#427bff"))
#let icon(value, size: 48pt) = text(font: "qweather-icons", size: size, fill: white)[#value]
#let panel(body, fill, inset: (top: 20pt, bottom: 20pt, left: 15pt, right: 15pt)) = block(width: 100%, fill: fill, radius: 15pt, inset: inset)[#body]
#let pollutant(item) = block(width: 100%)[
  #align(center)[
    #text(size: 20pt)[#item.value]
    #v(10pt)
    #box(width: 72pt, height: 5pt, fill: white, radius: 3pt)[
      #box(width: item.percent * 1%, height: 5pt, fill: rgb("#159447"), radius: 3pt)[]
    ]
    #v(10pt)
    #text(size: 20pt, fill: muted)[#item.label]
  ]
]

#set page(width: 750pt, height: auto, margin: 13.5pt, fill: page-bg)
#set text(font: ("Microsoft YaHei", "Noto Sans CJK SC", "Arial"), size: 10pt, fill: white, lang: "zh")
#set par(leading: 0.9em, spacing: 0pt)

#let current = data.now
#panel([
  #grid(
    columns: (1fr, 1fr),
    gutter: 20pt,
    [
      #pad(left: 52pt)[
        #align(left)[
        #text(size: 30pt, weight: "bold")[#data.city]
        #linebreak()
        #v(18pt)
        #text(size: 68pt)[#current.temp°]
        ]
      ]
    ],
    [
      #pad(right: 40pt)[
        #align(right)[
        #text(size: 14pt, fill: muted)[#data.updated_at]
        #linebreak()
        #icon(current.icon, size: 70pt)
        #linebreak()
        #text(size: 24pt)[#current.text]
        ]
      ]
    ],
  )
  #v(9pt)
  #block(fill: rgb("#0000001e"), radius: 15pt, inset: (top: 24pt, bottom: 24pt, left: 20pt, right: 20pt))[
    #grid(
      columns: (1fr, 1fr, 1fr, 1fr),
      gutter: 8pt,
      [#align(center)[#text(size: 23pt)[#current.wind_scale] #linebreak() #text(size: 23pt, fill: muted)[#current.wind_dir]]],
      [#align(center)[#text(size: 23pt)[#current.humidity%] #linebreak() #text(size: 23pt, fill: muted)[相对湿度]]],
      [#align(center)[#text(size: 23pt)[#current.precip]mm #linebreak() #text(size: 23pt, fill: muted)[降水量]]],
      [#align(center)[#text(size: 23pt)[#current.visibility]km #linebreak() #text(size: 23pt, fill: muted)[能见度]]],
    )
  ]
], today-bg)

#if data.warnings.len() > 0 [
  #v(15pt)
  #panel([
    #text(size: 17pt, weight: "bold")[天气预警]
    #v(5pt)
    #for warning in data.warnings [
      #text(size: 15pt, weight: "bold")[#warning.title]
      #v(2pt)
      #text(size: 11pt)[#warning.text]
      #v(6pt)
    ]
  ], gradient.linear(rgb("#b78c579d"), rgb("#f2d5b2b6")))
]

#if data.air != none [
  #v(15pt)
  #panel([
    #align(center)[
      #box(fill: rgb(data.air.color), radius: 18pt, inset: (top: 4pt, bottom: 4pt, left: 24pt, right: 24pt))[
        #text(size: 20pt)[#data.air.aqi #data.air.category]
      ]
      #if data.air.effect != "" [
        #v(5pt)
        #text(size: 10pt)[#data.air.effect]
      ]
    ]
    #v(18pt)
    #grid(
      columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
      gutter: 7pt,
      ..data.air.pollutants.map(item => pollutant(item)),
    )
  ], air-bg)
]

#v(15pt)
#panel([
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    gutter: 4pt,
    ..data.hourly.map(hour => block(width: 100%)[
      #align(center)[
        #text(size: 18pt)[#hour.temp°]
        #v(4pt)
        #box(width: 7pt, height: 75pt)[
          #align(bottom)[#box(width: 7pt, height: hour.temp_percent * 0.75pt, fill: rgb("#427bff"), radius: 4pt)[]]
        ]
        #v(4pt)
        #icon(hour.icon, size: 45pt)
        #v(2pt)
        #text(size: 17pt)[#hour.time]
      ]
    ]))
  )
], hours-bg)

#v(15pt)
#panel([
  #for day in data.daily [
    #grid(
      columns: (1fr, 1.25fr, 260pt, 1.25fr),
      gutter: 50pt,
      [#pad(left: 22pt)[#align(left)[#text(size: 22pt)[#day.weekday]
        #linebreak()
        #text(size: 15pt, fill: muted)[#day.date]]]],
      [#align(right)[#text(size: 30pt)[#day.temp_max°]
        #linebreak()
        #text(size: 22pt)[#day.text_day]]],
      [
        #grid(columns: (1fr, 1fr), [#align(center)[#icon(day.icon_day, size: 45pt)]], [#align(center)[#icon(day.icon_night, size: 45pt)]])
        #v(5pt)
        #box(width: 100%, height: 7pt, fill: temp-line, radius: 4pt)[]
      ],
      [#align(left)[#text(size: 30pt)[#day.temp_min°]
        #linebreak()
        #text(size: 22pt)[#day.text_night]]],
    )
    #v(28pt)
  ]
], days-bg, inset: (top: 20pt, bottom: 20pt, left: 15pt, right: 38pt))
