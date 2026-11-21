# 퀀트 전략 프로젝트용 저널 논문

조사 범위는 2024년 1월 1일~2026년 11월 21일의 The Journal of Finance (JF), The Review of Financial Studies (RFS), Journal of Financial Economics (JFE)다. 제목과 초록에서 선별한 **전략 후보 9편과 백테스트 검증 참고 3편**이다. 아래 팀 실험은 초록을 바탕으로 제안한 가설이다. 원 논문을 재현할 때는 본문에서 표본·거래 시점·포트폴리오 구성 규칙을 확인한다. 공개 PDF 중 일부는 게재본 이전 판본이므로 최종 인용에는 저널 DOI를 사용한다. 직접 PDF 응답을 확인한 항목은 PDF로, 나머지는 PDF를 제공하는 SSRN 논문 페이지로 연결한다.

## 전략 후보

| 논문 | 초록의 결과 | 팀 실험과 필요한 데이터 | 공개 원문 |
| --- | --- | --- | --- |
| RFS 2025 · [Short-Term Reversals and Longer-Term Momentum around the World: Theory and Evidence](https://doi.org/10.1093/rfs/hhaf057) | 짧은 투자 기간의 반전이 기간이 길어지면서 모멘텀으로 바뀐다. | **기존 CRSP로 시작.** 직전 한 달 수익률과 직전 한 달을 제외한 과거 12개월 수익률로 각각 종목을 정렬해 다음 달 성과를 비교한다. | [SSRN 공개본 및 PDF](https://ssrn.com/abstract=4069575) |
| JFE 2025 · [The Volatility Puzzle of the Beta Anomaly](https://doi.org/10.1016/j.jfineco.2025.103994) | 시장 변동성이 낮았던 달 이후 시장 노출을 맞춘 저베타 매수·고베타 매도 전략의 성과가 높았다. | CRSP와 시장 수익률을 사용한다. 과거 자료로 베타와 시장 변동성을 추정하고, 변동성 구간별 전략 성과를 비교한다. | [SSRN 공개본 및 PDF](https://ssrn.com/abstract=3882108) |
| RFS 2025 · [Earnings Extrapolation and Predictable Stock Market Returns](https://doi.org/10.1093/rfs/hhaf020) | 분기 첫 달의 시장 수익률과 이후 수익률의 관계가, 이후 달도 분기 첫 달인지에 따라 달라진다. | 월별 시장지수로 달력 규칙을 평가하고, 규칙을 정한 기간과 실제 성과를 평가하는 기간을 구분한다. | [SSRN 공개본 및 PDF](https://ssrn.com/abstract=3480863) |
| RFS 2026 · [What Drives Momentum and Reversal? Evidence from Day and Night Signals](https://doi.org/10.1093/rfs/hhag036) | 장중 수익률로 정렬한 포트폴리오에는 모멘텀이 있었지만 야간 수익률로 정렬한 경우에는 나타나지 않았다. | 일별 시가·종가를 확보해 장중, 야간, 종가 기준 모멘텀을 비교한다. | [SSRN 공개본 및 PDF](https://ssrn.com/abstract=4069509) |
| JF 2024 · [Anomaly Time](https://doi.org/10.1111/jofi.13372) | 여러 이상현상의 수익률이 정보 공개 직후 첫 달에 집중됐다. | 실제 공시일이 있는 재무 신호 하나를 골라 공시 직후 갱신과 정기 갱신을 비교한다. | [Wharton 공개 PDF](https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2019/09/Anomaly-Time.pdf) · [후속 공개본](https://ssrn.com/abstract=3069026) |
| JFE 2026 · [Dual Peer Effects and Cross-Stock Predictability](https://doi.org/10.1016/j.jfineco.2026.104274) | 경제적으로 연결된 기업들의 정보로 만든 지표가 개별 종목의 이후 수익률을 예측했다. | 산업 분류를 확보해 같은 산업 내 다른 종목의 수익률을 신호로 만들고, 기존 종목 모멘텀에 더했을 때 효과가 있는지 본다. | [Cambridge 공개 PDF](https://api.repository.cam.ac.uk/server/api/core/bitstreams/ed2431ba-8012-4d5e-8d39-2b3dc0954940/content) |
| JF 2025 · [War Discourse and the Cross Section of Expected Stock Returns](https://doi.org/10.1111/jofi.13482) | 뉴스에서 추출한 전쟁 담론으로 만든 팩터가 종목 간 기대수익률 차이를 설명했다. | 공개 시점이 확인되는 뉴스로 주제별 언급량을 만들고, 주제에 대한 민감도별로 이후 수익률을 비교한다. | [NBER 공개 PDF](https://www.nber.org/system/files/working_papers/w31348/w31348.pdf) |
| JFE 2026 · [Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models](https://doi.org/10.1016/j.jfineco.2026.104335) | 뉴스 제목에 부여한 LLM 점수가 최초 가격 반응 이후의 추가 움직임을 예측했다. | 뉴스 제목·공개 시각·가격으로, 거래 가능한 시점부터 이후 성과를 측정하고 단순 감성 점수와 LLM 점수를 비교한다. | [arXiv 공개 PDF](https://arxiv.org/pdf/2304.07619) |
| JFE 2025 · [Machine Learning from a “Universe” of Signals: The Role of Feature Engineering](https://doi.org/10.1016/j.jfineco.2025.104138) | 폭넓은 재무 신호로 만든 전략은 표본 밖에서도 예측력이 있었으나, 선별된 신호를 쓴 기존 연구보다 성과가 약했다. | 당시 이용 가능했던 재무자료로 소수의 신호를 단순 평균한 전략과 머신러닝으로 합친 전략을 비교한다. | [저자 공개 PDF](https://www.lehigh.edu/~xuy219/research/JFE_2025.pdf) |

## 백테스트 검증 참고

| 논문 | 확인할 항목 | 공개 원문 |
| --- | --- | --- |
| JF 2025 · [Pockets of Predictability: A Replication](https://doi.org/10.1111/jofi.13484) | **미래 정보 누출.** 예측 시점 이후의 데이터를 쓰는 오류를 정정하자 원 연구의 주요 결과가 약해졌다고 보고한다. 팀 실험에서 예측일마다 사용 가능한 데이터 범위를 기록한다. | [SSRN 공개본 및 PDF](https://ssrn.com/abstract=4710577) |
| JF 2025 · [Anomalies and Their Short-Sale Costs](https://doi.org/10.1111/jofi.13501) | **공매도 비용.** 초록에서 162개 이상현상의 평균 월 롱숏 수익률을 대차 수수료 전 +0.14%, 후 −0.01%로 보고한다. 팀 결과에 매수·매도 각각의 성과와 대차비용 가정을 표시한다. | [SSRN 공개본 및 PDF](https://ssrn.com/abstract=4266059) |
| RFS 2026 · [Machine Learning and the Implementable Efficient Frontier](https://doi.org/10.1093/rfs/hhag022) | **회전율과 거래비용.** 저자들은 거래비용을 포트폴리오 구성 단계에 반영한다. 팀 실험에서는 재조정 주기를 바꿨을 때 거래비용 차감 후 성과가 어떻게 달라지는지 본다. | [SSRN 공개본 및 PDF](https://ssrn.com/abstract=4187217) |

별도로 검토할 미출판 연구는 [워킹페이퍼 후보 목록](quant-working-papers.md)에 있다.
