#### [Back](Home.md)

## Contents
- [Architecture Background](#architecture-background)
	- [Problem Background](#problem-background)
		- [System Overview](#system-overview)
		- [Context](#context)
		- [Driving Requirements](#driving-requirements)
			- [Functional requirements](#functional-requirements)
			- [Quality attributes](#quality-attributes)
				- [Funcionalidade](#funcionalidade)
				- [Usabilidade](#usabilidade)
				- [Confiabilidade (Reliability)](#confiabilidade-reliability)
				- [Desempenho (Performance)](#desempenho-performance)
				- [Suportabilidade](#suportabilidade)
				- [Design constraints](#design-constraints)
				- [Implementation constraints](#implementation-constraints)
				- [Interface constraints](#interface-constraints)
				- [Physical constraints](#physical-constraints)
	- [Solution Background](#solution-background)
		- [Architectural Approaches](#architectural-approaches)
		- [Analysis Results](#analysis-results)
		- [Mapping Requirements to Architecture](#mapping-requirements-to-architecture)

# Architecture Background
>Architecture Background provides information about the software architecture, by:
>- describing the background and rationale for the software architecture;
>- explaining the constraints and influences that led to the current architecture;
>- describing the major architectural approaches that have been utilized in the architecture.
  
## Problem Background

### System Overview and Context

This documentation outlines the development of an advanced system aimed at forecasting stock market data through the integration of news and social media sentiment analysis. The primary objective of this project is to provide reliable predictions of stock market trends, focusing particularly on North American companies. By leveraging the vast amounts of data from news sources and social media platforms, our innovative technology offers invaluable insights into future market trajectories.

Furthermore, this project includes the creation of a sophisticated portfolio recommendation model, which uses the forecasts generated from sentiment analysis to guide investors in making informed decisions. The correlation between sentiment patterns and market movements has been thoroughly examined and validated, proving the system's accuracy and effectiveness.

With its potential to revolutionize investment strategies, this research has far-reaching implications for the financial industry. Emphasizing data-driven decision-making, the system empowers investors to capitalize on timely and precise market predictions. As I present the outcomes of extensive testing and validation, I envision the work shaping the future of investment practices and contributing to a data-centric paradigm in financial markets.

### Driving Requirements
> This section lists the functional requirements, quality attributes and design constraints. It may point to a separate requirements document.

#### Functional requirements
1. As an user, I want to obtain a company stock value forecast, providing me insights into potential stock trends.
2. As a user, I want the system to generate personalized portfolio recommendations that align with my investment preferences and risk tolerance, in order to help make informed investment decisions.
3. As an admin, I want to easily configure and update the constants without affecting the overall system functionality.
4. As an admin, I want the ability to add, modify, or remove AI models used for stock market data forecasting to continuously improve the accuracy of the system's predictions.
5. As an admin, I want the capability to adjust various constants and parameters used in the AI algorithms to fine-tune the forecasting model and optimize its performance.


![Use Case Diagram](diagrams/level1/L1_UseCaseDiagram.svg)

#### Quality attributes
The quality attributes are categorized and systematized according to the model [FURPS+](https://web.archive.org/web/20201112020231/http://www.ibm.com/developerworks/rational/library/4706.html#N100A7).

##### Functionality
1. Each system will only be able to access the data that concerns it.

2. The integrity of the information accessed by the systems must be audited and verified.

##### Usability
3. For a first version there will be no Login/ Registration module. Anyone can make the REST requests.

4. Under the current project, the admininstration tasks can be done directly in the database and a management module is not required.

##### Reliability
5. The forecasts must be above 50% win rate and beat the market.

##### Performance
n/a

##### Supportability
6. Although not in the current scope of the project, future extension to mobile applications should be taken into account in the solution architecture.

7. The system must be easily maintanable. The external sources of information can change and the application must be ready to adapt.

##### Design constraints
8. The main functionalities of each module are as follows:

	- **AI Stock Picker** – Allows the computation of the predictions, as the persistence of the results into a database (InfluxDB).
	- **UI** – User Interface

##### Implementation constraints
n/a

##### Interface constraints
n/a

##### Physical constraints
9. There are two servers:

	- **InfluxDB**: Timeseries-data storage 
	- **SQLite**: Other data storage (constants, models to use, etc..)

10. Some of the applications should be deployed *on premises* and others in IaaS and PaaS (*on cloud*).

## Solution Background

### Architectural Approaches

Based on the non-functional requirements and design constraints, the following approaches/patterns/styles will be adopted:

- Client-Server, because the module AIStockPicker is an application server for the UI;
- Web Application, where the frontend is performed by a SPA (Single Page Application), and the backend is performed by the AI StockPicker module;
- SOA, because the server should provide API, and particularly API to be used on the web, provided services to the respective clients. Level 0, 1 and 2 of the [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html) applied to REST will be adopted.
- Layered architecture, more specifically Onion Architecture, since provides several benefits, including separation of concerns, testability, maintainability, flexibility, and scalability.

### Analysis Results

No analysis or evaluation results are available for the moment. Qualitative studies about the adopted styles/patterns (namely Onion in AIStockPicker, but also Dependency Injection in UI), allow empirically to advocate that maintainability, evolutability and testability of the software are high, while allowing to achieve the desired functionalities.
