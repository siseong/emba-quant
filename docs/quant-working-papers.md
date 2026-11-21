# 퀀트 전략 프로젝트용 워킹페이퍼

2026년 11월 21일 확인. 세 논문의 제목·초록을 바탕으로 정리했다. 논문이 보고한 결과와 팀이 검증해볼 가설을 각각 적었다. 아래의 팀 실험은 모두 재현 전이며, 논문의 원래 설정과 일치하는지는 본문에서 확인해야 한다.

## 1. 주식 순위에 예측 불확실성 반영

**Uncertainty-Adjusted Sorting for Asset Pricing with Machine Learning** — Yan Liu, Ye Luo, Zigan Wang, Xiaowei Zhang.

- 버전·상태 — arXiv v1, 2026-01-02. 저자 연구 목록에서 워킹페이퍼로 분류하며, 정식 저널 게재는 확인되지 않았다. [초록](https://arxiv.org/abs/2601.00593v1) · [공개 PDF](https://arxiv.org/pdf/2601.00593v1) · [저자 연구 목록](https://www.siem.sem.tsinghua.edu.cn/yanliu-homepage/index.html) · [라이선스 CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)
- 초록 — 미국 주식의 예상 수익률 자체로 정렬하는 방식과 예측의 불확실성을 반영한 경계값으로 정렬하는 방식을 비교했다. 저자들은 성과 개선이 주로 변동성 감소에서 비롯됐다고 보고한다.
- 팀 실험 — 수업의 12개월 모멘텀을 기준 전략으로 두고, 과거 자료만으로 추정한 불확실성을 정렬 점수에 반영했을 때 이후 수익률과 샤프비율이 개선되는지 본다. 종목별 실현 변동성을 대용치로 쓰는 간단한 실험과 논문의 예측 불확실성 추정은 구분한다. 첫 실험은 수업용 CRSP 월별 수익률로 시작할 수 있다.

## 2. 단기 추세추종이 약해지는 조건

**Is Trend Still Your Friend? A Microstructural Account of the Demise of Short-Term Trend-Following** — Jutta G. Kurth, Zoltan Eisler, Adam Rej, Jean-Philippe Bouchaud.

- 버전·상태 — arXiv v1, 2026-07-02. 정식 저널 게재는 확인되지 않았다. [초록](https://arxiv.org/abs/2607.01550v1) · [공개 PDF](https://arxiv.org/pdf/2607.01550v1) · [라이선스 CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 초록 — 저자들은 약 100개 유동성 높은 선물 계약에서 금융위기 이후 추세추종 전략의 성과 저하가 변동성 대비 호가 단위가 작은 계약에 집중됐다고 보고한다.
- 팀 실험 — 선물별 단기·장기 추세 신호를 만들고, 변동성 대비 호가 단위가 작은 그룹과 큰 그룹의 성과를 비교한다. 선물 가격과 계약별 최소 호가 단위가 필요하다. 주식 월별 데이터로 신호 기간만 비교하는 실험은 별도의 확장 실험으로 표시한다.

## 3. 이미 예상할 수 있었던 내용을 제거한 뉴스 신호

**The Inefficient Pricing of News** — Antoine Didisheim, Bryan T. Kelly, Mohammad Pourmohammadi, Hanqing Tian.

- 버전·상태 — NBER Working Paper 35093, 2026년 4월 공개, 2026년 5월 개정. 정식 저널 게재는 확인되지 않았다. [초록과 버전 이력](https://www.nber.org/papers/w35093) · [공개 PDF](https://www.nber.org/system/files/working_papers/w35093/w35093.pdf) · [저자 연구 목록](https://www.bryankellyacademic.org/)
- 초록 — 기존 종목 특성으로 예측되는 뉴스 내용을 제거한 뒤 남은 정보가, 원래 뉴스보다 이후 수익률을 더 잘 예측했다고 보고한다.
- 팀 실험 — 같은 질문을 커뮤니티 글에 적용한다. 글의 감성이나 언급량으로 만든 원래 점수와, 직전 수익률·변동성·시가총액으로 설명되는 부분을 제거한 점수를 비교한다. 종목과 게시 시각을 연결할 수 있는 텍스트, 해당 시점의 종목 특성과 이후 수익률이 필요하다. 신호는 게시 이후 실제 거래할 수 있는 시점에만 사용한다.

PDF는 원본 공개처에서 읽는다. 복제본을 별도로 공유해야 할 경우에는 해당 판본의 라이선스와 재배포 조건을 확인한다.
