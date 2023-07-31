#### [Back](Home.md)

## Contents
- [Documentation Roadmap and Overview](#documentation-roadmap-and-overview)
	- [Purpose and Scope of the SAD](#purpose-and-scope-of-the-sad)
	- [How the SAD Is Organized](#how-the-sad-is-organized)
	- [How a View Is Documented](#how-a-view-is-documented)

# Documentation Roadmap and Overview

> Sub-parts of this section provide information that will help readers or users of the Software Architecture Document (SAD) quickly find information that will enable them to do their jobs. Readers of the SAD seeking an overview should begin here, as should readers interested in finding particular information to answer a specific question.

## Purpose and Scope of the SAD

>This SAD describes the software's architecture of the AI Stock Picker system, developed in the interest of a master's thesis.
>In this document, all the documentation on the implementation of the project can be assessed.

## How the SAD Is Organized
>This section provides a narrative description of the six major sections of the SAD and the overall contents of each. Readers seeking specific information can use this section to help them locate it more quickly.
>This SAD is organized into the following seven sections:
> 1. This Documentation Roadmap and Overview provides information about this document and its intended audience. It provides the roadmap and document overview.
> 2. Architecture Background provides information about the software architecture. It describes the background and rationale for the software architecture. It explains the constraints and influences that led to the current architecture, and it describes the major architectural approaches that have been utilized in the architecture.
> 3. Views and
> 4. Mapping Between Views; both specify the software architecture.
> 5. Referenced Materials, provides look-up information for documents that are cited elsewhere in this SAD.
> 6. Glossary and Acronyms is an index of architectural elements and relations giving their definition, and where each is used in this SAD.


## How a View Is Documented
>1. Primary Presentation
>> 1. Is usually graphical
>> 2. Should include a key that explains the notation
>> 3. Shows elements and relations among them
>> 4. Shows the information you want to convey about the view first
>> 5. Should identify elements that are external to scope of the view (if external entities are not clearly marked in the diagram, consider adding a context diagram)
> 2. Element Catalog
>>	- Explains elements depicted in primary presentation and their properties
>>	- Is usually a table with element name and textual description
>>	- May contain interface documentation
>>	- May contain behavior documentation
> 3. Variability Guide
>>	- Points where system can be parameterized or reconfigured. Examples:
>>		- Number of instances in a pool
>>		- Support for plug-ins or add-ons
>>		- Support for different versions of OS, database server or runtime environment
>>	- Maybe the view is a reference architecture
>>		- Provide guidelines to instantiate it
> 4. Other Information
>>	- Description and rationale for important design decisions (including relevant rejected alternatives)
>>	- Results of analysis, prototypes and experiments
>>	- Context diagram
> 5. Parent View
>>	- If the current view is the refinement of another view, indicate which one

In this SAD the UML notation will be adopted, namely (but not exclusively) component, sequence, package and node diagrams. This guarantees 1.1, 1.2 and 1.3.

The organization of views by combining the C4 model (different levels of abstraction/granularity) and the 4+1 views model (various points of view of the architecture) allows addressing requirement 1.4.

By adopting the C4 model, requirement 1.5 is addressed.