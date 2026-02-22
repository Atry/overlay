# Overlay Language Specification

## 1. Introduction

The Overlay language is a programming language designed to facilitate the flexible composition and configuration of logic and data structures through the use of _overlays_. Unlike traditional programming languages that use classes or functions as the primary building blocks, the Overlay language employs a unified concept where everything is represented as an overlay. This approach allows for greater modularity, reusability, and flexibility.

The Overlay language is a lazily-evaluated, immutable language, meaning that values are only computed when necessary, and once created, they cannot be changed. This design makes the Overlay language particularly well-suited for applications that require functional purity, such as configuration management, domain-specific language (DSL) creation, and code generation.

The Overlay language is not limited to a specific platform or target language. It can generate code for multiple languages by representing abstract syntax trees (ASTs) that correspond to various programming languages. This makes the Overlay language an ideal choice for scenarios involving cross-language interoperability, complex configuration files, and even software synthesis.

### 1.1 Comparison with Other Languages

#### 1.1.1 Object-Oriented Languages

In traditional object-oriented languages like Java or C++, classes and objects are used to encapsulate state and behavior. However, this approach has several limitations that the Overlay language addresses through its unique design:

- **Complex Inheritance Hierarchies**: Object-oriented languages often require complex class hierarchies to represent different behaviors, leading to rigidity and difficulty in maintenance. Multiple inheritance, in particular, can introduce the "diamond problem," where the same method or property is inherited from multiple sources, causing ambiguity and conflicts.

  - **the Overlay language Solution**: the Overlay language uses a flexible composition model where overlays can be combined and inherited without conflict. Properties are automatically merged, and there is no need for complex inheritance trees. This eliminates the diamond problem and allows for clean, modular inheritance structures.

- **Static and Inflexible Object Models**: Once a class is defined in an object-oriented language, its structure and behavior are fixed. Modifying or extending the behavior often requires creating subclasses or using design patterns like decorators, which can add complexity and reduce clarity.

  - **the Overlay language Solution**: Overlays in the Overlay language can be dynamically composed and configured, allowing for flexible adjustments without altering existing definitions. This dynamic composition model enables developers to easily modify and extend behavior by combining overlays, without the need for static class hierarchies or complex design patterns.

- **Method Overriding and the Risk of Ad Hoc Behavior**: Traditional object-oriented languages rely on method overriding to modify inherited behavior. This can lead to unpredictable behavior, especially in deep inheritance hierarchies, where methods in subclasses may inadvertently override those in parent classes, introducing subtle bugs.

  - **the Overlay language Solution**: the Overlay language does not support method overriding. Instead, it merges properties from multiple parent overlays, ensuring that all inherited properties coexist without conflict. This approach avoids the risks associated with method overriding, such as accidental method shadowing or breaking polymorphic behavior, providing a more predictable and safer inheritance model.

- **Overreliance on Design Patterns**: To address limitations in object-oriented design, developers often resort to complex design patterns like Singleton, Factory, and Strategy. While these patterns solve specific problems, they can introduce additional complexity and boilerplate code.

  - **the Overlay language Solution**: the Overlay language can be seen as a metaprogramming language designed to generate code for other languages. Instead of using design patterns to address language limitations, developers can use the Overlay language to generate consistent and reusable code across multiple languages. By representing abstract syntax trees (ASTs) and configurations as overlays, the Overlay language allows for the creation of domain-specific languages (DSLs) and the automated generation of language constructs, reducing the need for complex design patterns and enabling more expressive and maintainable code.

Overall, the Overlay language provides a more modular and flexible alternative to traditional object-oriented languages by using overlay composition instead of class inheritance. Its support for property merging and dynamic composition allows developers to build complex systems more easily and safely. As a metaprogramming language, the Overlay language excels in generating code for multiple languages, making it a powerful tool for scenarios requiring cross-language interoperability and code generation.

#### 1.1.2 Functional Languages

Functional programming languages like Haskell and Scala emphasize immutability and functional purity, offering benefits such as easier reasoning about code and avoidance of side effects. However, they also come with certain limitations that the Overlay language addresses through its design:

- **Complexity of Function Composition Syntax**: Functional languages often use advanced and abstract syntax for function composition, such as higher-order functions, monads, and combinators. While powerful, these constructs can be difficult to read and understand, especially for those new to functional programming.

  - **the Overlay language Solution**: the Overlay language employs a more intuitive and declarative approach by representing logic and data structures through overlay composition and configuration. Using familiar data serialization formats like YAML or JSON, the Overlay language allows developers to define complex behaviors in a hierarchical and readable manner. This reduces the syntactic complexity associated with function composition in traditional functional languages.

- **Complexity of Context Management**: In functional programming, managing context, such as state or environment, often requires explicit passing of context through function parameters or using monads, which can make code verbose and harder to maintain.

  - **the Overlay language Solution**: the Overlay language simplifies context management by allowing overlays to automatically inherit and access properties from their lexical scope. This means that shared context or state can be accessed without the need for explicit parameter passing or complex monadic structures. The unified scoping and inheritance rules in the Overlay language reduce boilerplate code and make the logic more straightforward.

- **The Expression Problem**: The Expression Problem refers to the difficulty of extending both the set of data types and the set of operations over them in a type-safe and modular way. In functional languages, adding new data types is straightforward, but adding new operations can be challenging without modifying existing code.

  - **the Overlay language Solution**: the Overlay language addresses the Expression Problem by allowing both overlays (representing data types) and properties or methods (representing operations) to be extended and composed modularly. Since overlays can inherit and combine properties from multiple sources without conflicts, developers can add new data types and operations independently. This flexibility enables the Overlay language to support extensibility in both dimensions, overcoming the limitations faced in traditional functional programming languages.

Overall, the Overlay language provides a more accessible and flexible alternative to functional programming languages by reducing syntactic complexity, simplifying context management, and addressing the Expression Problem. Its overlay-based composition model allows for the modular and conflict-free extension of both data structures and operations, facilitating the development of complex systems in a more intuitive and maintainable way.

#### 1.1.3 Declarative Configuration Languages

Declarative configuration languages like JSON, YAML, and Nix are widely used to represent static data and configurations. They offer simplicity and readability but often lack the ability to express dynamic logic and complex relationships. the Overlay language extends these ideas, providing a more powerful and flexible alternative.

- **Static Configuration Limitations**: Traditional configuration languages like JSON and YAML are limited to representing static data structures. They cannot express dynamic relationships or logic, such as conditional values, calculations, or dependencies between configurations.

  - **the Overlay language Solution**: the Overlay language allows for dynamic logic and configuration through overlay composition and inheritance. Properties can be inherited, combined, or overridden based on context, enabling dynamic configurations that adapt to changing conditions. This makes the Overlay language suitable for scenarios where complex dependencies and conditional configurations are required.

- **Lack of Modularity and Reusability**: In static configuration formats, it is difficult to create modular and reusable components. While YAML supports features like anchors and aliases, these are limited and can lead to complex and error-prone configurations.

  - **the Overlay language Solution**: the Overlay language enables modular and reusable configuration components through its overlay system. Each overlay can encapsulate a piece of configuration or logic, which can then be combined and reused in different contexts. This modular approach not only improves maintainability but also allows for the creation of complex configurations by composing simpler, reusable overlays.

- **Difficulty in Representing Relationships**: Declarative configuration languages often lack the ability to represent complex relationships between different parts of a configuration. Dependencies and relationships must be managed manually, which can lead to errors and inconsistencies.

  - **the Overlay language Solution**: the Overlay language uses inheritance to represent relationships between overlays, enabling clear and maintainable configurations. By using a unified inheritance model, the Overlay language allows for the automatic resolution of dependencies and relationships, reducing the risk of errors and inconsistencies.

- **Limited Expressiveness for Code Generation**: While declarative languages like Nix provide some level of code generation through lazy evaluation and functional constructs, they are primarily designed for configuration management and package management. Extending them for general-purpose code generation or complex logical expressions can be cumbersome.

  - **the Overlay language Solution**: the Overlay language, as a metaprogramming language, is designed to generate code and configurations for multiple target languages. By representing abstract syntax trees (ASTs) and logical structures as overlays, the Overlay language can be used to generate code in different languages consistently. This capability makes the Overlay language ideal for building DSLs, automating code generation, and ensuring consistency across different language environments.

Overall, the Overlay language extends the capabilities of traditional declarative configuration languages by supporting dynamic logic, modularity, and complex relationships. Its overlay-based approach enables more expressive and maintainable configurations, and its metaprogramming capabilities make it a powerful tool for code generation and cross-language interoperability.

### 1.2 Key Use Cases

#### 1.2.1 Multi-language Code Generation

the Overlay language can generate code in multiple target languages, making it a versatile tool for building DSLs or serving as the core module of a compiler. By representing the ASTs of various languages as overlays, the Overlay language can translate a single logical structure into multiple programming languages, ensuring consistency and reducing duplication across projects.

#### 1.2.2 Cross-language Interoperability

the Overlay language provides a unified way to define data structures and logic that can be shared across different programming environments. For instance, a complex business logic model defined in the Overlay language can be translated into both a backend service in Scala and a frontend component in JavaScript, ensuring consistent behavior and data flow.

#### 1.2.3 Complex System Configuration

As a configuration language, the Overlay language excels in defining complex systems with interdependent components. Through the use of overlay composition and inheritance, configuration files can be modular, reusable, and adaptable, enabling powerful and flexible system configurations that go beyond the capabilities of traditional static formats like JSON or YAML.

### 1.3 A Simple Example

The following example demonstrates how to use the Overlay language to define a basic arithmetic operation represented as an AST:

```yaml
# math_operations.oyaml

Number:
  - {} # An overlay that represents a number type.

add:
  - [Number] # Inherits from the 'Number' overlay.
  - addend1: [Number] # Property 'addend1', which is a 'Number'.
  - addend2: [Number] # Property 'addend2', which is also a 'Number'.

multiply:
  - [Number] # Inherits from the 'Number' overlay.
  - multiplicand: [Number] # Property 'multiplicand', which is a 'Number'.
  - multiplier: [Number] # Property 'multiplier', which is also a 'Number'.
```

```yaml
# test.oyaml

example_calculation:
  - [add]
  - addend1:
      - [multiply]
      - multiplicand: 2
      - multiplier: 3
  - addend2: 4
```

**Explanation**:

1. The `Number` overlay represents a basic number type with no initial value, aligning with the Overlay language's immutable and lazy-evaluated nature.
2. The `add` overlay inherits from `Number` and defines two properties, `addend1` and `addend2`, both of which are also `Number`.
3. The `multiply` overlay defines a multiplication operation with two properties: `multiplicand` and `multiplier`.
4. In `test.oyaml`, the `example_calculation` overlay uses the `add` operation to add two numbers:
   - `addend1` is a multiplication of `2` and `3`, represented using the `multiply` overlay.
   - `addend2` is the constant `4`.

This example illustrates how the Overlay language can be used to represent complex logic in a modular and declarative manner. The `example_calculation` overlay serves as the root of an AST, with each operation (e.g., `add` and `multiply`) acting as nodes, and their properties (`addend1`, `addend2`, `multiplicand`, `multiplier`) as sub-nodes. This structure can be evaluated directly within the Overlay language or used to generate equivalent code in another language.

## 2. Overlay Definitions and Data Types

### 2.1 Basic Structure and Data Types

the Overlay language supports a range of data types, all of which map directly to JSON data types. These types form the foundational elements of the language and define how data is represented and manipulated within the Overlay language.

#### 2.1.1 Primitive Data Types

The primitive data types in the Overlay language correspond directly to JSON's scalar types:

- **Strings**: Represented as sequences of characters, corresponding to JSON strings.

  - Example: `"hello, world"`

- **Numbers**: Can be either integers or floating-point numbers, just like JSON numbers.

  - Example: `42`, `3.14`

- **Booleans**: Represent truth values, with `true` and `false` as the only valid values.

  - Example: `true`, `false`

- **Null**: Represents the absence of a value, similar to JSON `null`.
  - Example: `null`

#### 2.1.2 Overlays as Data Types

In the Overlay language, the primary data type is the overlay itself, which corresponds to JSON objects. Each overlay represents a collection of properties and can inherit from other overlays, enabling complex compositions and configurations.

- **Overlay**: Corresponds to a JSON object, with each key representing a property name and each value representing an overlay, primitive type, or an inheritance to another overlay.

  Example:

  ```yaml
  Number:
    - {} # An overlay with no properties, representing a number type.

  add:
    - [Number] # Inherits from the 'Number' overlay.
    - addend1: [Number] # Property 'addend1', which is a 'Number'.
    - addend2: [Number] # Property 'addend2', which is also a 'Number'.
  ```

  In this example:

  - The `Number` overlay serves as a base overlay with no initial properties.
  - The `add` overlay inherits from `Number` and introduces two new properties, `addend1` and `addend2`, both of which are of type `Number`.

#### 2.1.3 Relationship to JSON

the Overlay language's data types map directly to JSON types:

- **JSON Object → Overlay**: An overlay is defined by a JSON object where keys are property names, and values can be overlays or primitive data types.
- **JSON Scalar Types → Primitive Data Types**: JSON strings, numbers, booleans, and null values map directly to the Overlay language's corresponding primitive data types.

#### 2.1.4 No First-class List Support

Unlike JSON, the Overlay language does not support lists as a first-class type within the language itself. This means that you cannot directly define or manipulate lists in the core the Overlay language as you would in JSON. Instead, lists are defined and manipulated through the Overlay language standard library. This design choice maintains the simplicity and consistency of the language by focusing on overlay composition and inheritance. For scenarios requiring list-like structures or operations, the Overlay language encourages using custom overlays to represent collections or sequences of data.

### 2.2 Properties

Properties are the fundamental components of an overlay, defining its internal state or behavior. The value of a property can be one of the following types:

1. **Basic Data Types**: Strings, numbers, booleans, or null.
2. **Inheritance**: Properties can inherit other overlays by specifying their path, allowing for inheritance and reuse of existing overlays.

#### Property Definition Syntax

The definition of a property resembles key-value pairs in JSON or YAML. Unlike most programming languages, property names in the Overlay language do not need to be unique. If the same property name is defined multiple times, all definitions will always be automatically merged through multiple inheritance. This allows for the creation of complex and modular structures without conflict.

Example:

```yaml
Person:
  - name: [String] # Defines a 'name' property of type String
  - age: [Number] # Defines an 'age' property of type Number
  - is_married: [Boolean] # Defines an 'is_married' property of type Boolean
```

In this example, if `name` is defined again in a different overlay and both overlays are inherited, the resulting overlay will contain all definitions of `name`.

#### Nested Properties

Property values can be nested overlays, creating more complex structures. For example, we can define an `Address` property within the `Person` overlay:

```yaml
Address:
  - street: [String] # Defines a 'street' property
  - city: [String] # Defines a 'city' property
  - zip_code: [String] # Defines a 'zip_code' property

person_with_address:
  - [Person] # Inherits the 'Person' overlay
  - address: [Address] # Adds an 'address' property using the 'Address' overlay
```

In this example, the `person_with_address` overlay inherits from `Person` and includes a nested `address` property that inherits the `Address` overlay.

### 2.3 Inheritance

In the Overlay language, inheritance is the mechanism by which the current overlay inherits all properties and scalar values from another overlay. An inheritance is represented as an array of strings that indicate the path to the target overlay.

#### Grouping Property Definitions in Lists

When defining an overlay, you can optionally put properties in lists (i.e., using the `-` symbol in YAML) to indicate the hierarchical structure of properties. When an overlay inherits from other overlays, properties must be prefixed with `-` to avoid confusion between inheritance chains and property declarations. This prefix is optional when there is no inheritance.

**Why Use the `-` Prefix for Properties**

In YAML, a node must be either an array or an object; it cannot contain both array elements and object members simultaneously. Therefore, when an overlay inherits other overlays, the `-` prefix is required to clearly indicate that each property is an item in an array. This prefix is optional when there is no inheritance but is mandatory when inheritance is involved.

**Invalid YAML**:

```yaml
my_car:
  - [Vehicle]          # Inherits the 'Vehicle' overlay
  color: [String]    # Adds a new property 'color'
  doors: [Number]    # Adds a new property 'doors'
```

In the example above, the `my_car` node simultaneously contains an array element (`[Vehicle]`) and object members (`color` and `doors`), which violates the structural rules of YAML.

**Valid YAML**:

```yaml
my_car:
  - [Vehicle] # Inherits the 'Vehicle' overlay
  - color: [String] # Adds a new property 'color'
  - doors: [Number] # Adds a new property 'doors'
```

In this valid example, each element within the `my_car` node begins with the `-` prefix, indicating that these properties are part of an array. This allows the YAML parser to correctly interpret the structure of `my_car`.

#### Multiple Inheritance and Scalar Values

the Overlay language supports conflict-free multiple inheritance and allows scalar values to be inherited from multiple sources. This means an overlay can combine properties and scalar values from multiple parent overlays without any conflict. All inherited properties and values are integrated seamlessly, resulting in a unified set of properties for the child overlay.

**Example of Multiple Inheritance with Scalar Values**

The Overlay language allows scalar values to coexist and be inherited along with other properties, as shown below:

```yaml
Number:
  - {} # Defines an empty number type overlay

my_number:
  - 42 # Defines the scalar value 42
  - [Number] # Inherits the 'Number' overlay
```

In this example, `my_number` has both a scalar value `42` and inherits the `Number` type overlay, demonstrating that scalar values and type overlays can coexist and be inherited together.

**Conflict-Free Inheritance**

In the Overlay language, properties with the same name defined in multiple parent overlays are always automatically merged:

```yaml
# basic_features.oyaml
Vehicle:
  - wheels: [Number]
  - engine: {}

Motor:
  - engine:
      gasoline: true # Defines a default scalar value for 'engine'

# advanced_features.oyaml
hybrid_car:
  - ["basic_features", Vehicle]
  - ["basic_features", Motor]
  - wheels: 4 # Defines the scalar value for 'wheels'
  - engine:
      hybrid: true # Defines the scalar value for 'engine'
  - battery_capacity: 100 # Adds a new 'battery_capacity' property
```

In this example, `hybrid_car` inherits the `engine` property from both `Vehicle` and `Motor`. Instead of a conflict, the properties are merged, along with its extra property `hybrid`, which the child overlay explicitly defines. The `battery_capacity` property is added uniquely to `hybrid_car`.

## 3. Syntax and Grammar

### 3.1 Lexical Structure

the Overlay language is a language that leverages the lexical structures of JSON, YAML, and TOML, focusing on their ability to represent structured data in a clear and readable manner. This section outlines the core syntax and grammar of the Overlay language, emphasizing its usage of these formats and how they correspond to the Overlay language's data and logic constructs.

The Overlay language does not have its own unique lexical structure; instead, it directly adopts the lexical structures of JSON, YAML, and TOML. This means that any syntax that can be converted into JSON is valid in the Overlay language. Specifically:

- **JSON**: Fully supported, including all standard JSON types and structures.

- **YAML**: Supported as long as it can be losslessly converted into JSON. This means that only a subset of YAML is used, excluding features such as:

  - **Anchors and Aliases**: YAML constructs like `&` (anchor) and `*` (alias) are not supported as they cannot be directly represented in JSON.
  - **Tags**: YAML's type tags (e.g., `!!str`, `!!int`) are not supported, as the Overlay language uses its own data type system.
  - **Complex Data Types**: Data types like sets, timestamps, and ordered mappings are not supported.

- **TOML**: Supported in its JSON-compatible subset, which includes basic data types like strings, finite numbers, booleans, and dates, but excludes date/time datatypes.

By utilizing these existing formats, the Overlay language ensures a seamless integration with widely-used data serialization standards, making it easy to define complex data structures and configurations.

#### 3.1.1 Examples of Supported and Unsupported Syntax

**Supported JSON Syntax**:

```json
{
  "name": "example",
  "value": 42,
  "is_active": true,
  "data": null
}
```

**Supported YAML Syntax**:

```yaml
name: example
value: 42
is_active: true
data: null
```

**Unsupported YAML Syntax** (anchors and aliases):

```yaml
base: &base_value
  name: example

derived:
  <<: *base_value
  value: 42
```

**Supported TOML Syntax**:

```toml
name = "example"
value = 42
is_active = true
```

**Unsupported TOML Syntax** (time):

```toml
data = 23:22:21.0123
```

## 4. File Structure and Formats

### 4.1 Supported File Formats

the Overlay language supports the following file formats for representing source code:

- **YAML**: File extension `.oyaml`.
- **JSON**: File extension `.ojson`.
- **TOML**: File extension `.otoml`.

The Overlay language uses these formats to define overlays in a structured and human-readable manner. The formats share the following characteristics:

1. **JSON Compatibility**: All supported formats must be serializable to JSON. This means that only the subset of YAML and TOML that can be converted to JSON without loss of information is supported.

2. **File Extensions**: The file extension must indicate the format and its use as an Overlay file: `.oyaml`, `.ojson`, or `.otoml`.

3. **Lossless Conversion**: The language only uses features that can be converted between the supported formats without loss of information.

### 4.2 File and Overlay Naming Conventions

#### 4.2.1 File Naming Conventions

- **Format**: Use lowercase letters with underscores to separate words. File names must use the `.o` prefix before the format extension (e.g., `.oyaml`, `.ojson`, `.otoml`) to indicate they are Overlay files.

- **Type Definition**: Use singular nouns if defining a primary concept (e.g., `vehicle.oyaml`). Use plural nouns if the file contains multiple instances or variations (e.g., `vehicles.oyaml`).

**Examples**:

- `vehicle.oyaml`
- `vehicles.oyaml`
- `test_cases.ojson`

#### 4.2.2 Overlay Naming Conventions

Overlay names within files must follow these conventions based on their intended use:

1. **Type-like Overlays**:

   - Use UpperCamelCase naming (e.g., `PersonDetails`, `Vehicle`). These overlays represent types and can be inherited by other overlays.
   - Should not include scalar values; instead, focus on defining structured data or behaviors.

2. **Value-like Overlays**:

   - Use lowercase with underscores (e.g., `height_value`, `name`). These overlays typically represent individual values or instances and may include scalar values.

3. **Instance Overlays**:

   - Use lowercase with underscores (e.g., `electric_vehicle`, `combined_person`) to represent specific instances or configurations and may inherit from multiple type-like overlays.

### 4.3 Cross-File Inheritance

the Overlay language allows inheriting overlays defined in different files. The rules for cross-file inheritance are as follows:

1. **Inheritance Format**:

   - An inheritance is represented as an array of strings, where each string corresponds to a segment in the path to the target overlay.
   - The format for cross-file inheritance is `[path, to, overlay_name]`, where `path` is the relative path from the current file to the target overlay, excluding the top-level directory name.

2. **Directory Scope**:

   - Each directory has its own lexical scope. Files within the same directory can inherit each other using just the file name and overlay name (e.g., `[file_name, overlay_name]`).
   - Directories do not share scopes, meaning that an overlay defined in one directory cannot directly inherit a sibling directory's overlay without specifying the correct path.

3. **Lexical Scope Resolution**:

   - the Overlay language automatically searches for inheritances starting in the current directory. If not found, it searches in the parent directory, and then the parent's parent directory, continuing upwards until the root is reached.
   - The first segment of the inheritance looks for the overlay name in the current lexical scope, which includes:

     - **Current File**: Overlays defined in the same file.
     - **Parent Overlays**: Overlays in the parent scope of the current overlay.
     - **Directory Scope**: Overlays defined directly in the current directory.

   - Subsequent segments can access properties in the inherited overlay hierarchy if the first segment resolves to an overlay in the scope.

4. **Isolated File Scopes**:

   - Overlays defined in separate files within the same directory do not share lexical scopes with each other. They can only access overlays from the directory scope and their own file.

5. **No `..` Syntax for Parent Directory**:

   - the Overlay language does not support the `..` syntax to navigate to parent directories. Instead, the language automatically searches upward through the directory structure, starting from the current directory.

#### 4.3.1 Example of Cross-File Inheritance

**Directory Structure**:

```
project/
│
├── module/
│   ├── vehicle.oyaml
│   ├── electric.oyaml
│   └── car.oyaml
│
├── config/
│   └── settings.oyaml
└── test/
    └── test_car.oyaml
```

**vehicle.oyaml**:

```yaml
Vehicle:
  engine: {}
  wheels: [Number]
```

**electric.oyaml**:

```yaml
Electric:
  - engine:
      electric: true
  - battery_capacity: [Number]
```

**car.oyaml**:

```yaml
Car:
  - [Vehicle]
  - [Electric]
  - model: [String]
```

**test_car.oyaml**:

```yaml
test_car:
  - [module, Car] # Cross-directory inheritance to Car in module/car.oyaml
  - model: "Test Model"
  - test_battery:
      - [module, Electric, battery_capacity] # Inheritance to battery_capacity in Electric
```

In this example:

- The `test_car` overlay in `test_car.oyaml` inherits `Car` and `Electric` from the `module` directory using the format `[module, Car]` and `[module, Electric, battery_capacity]`.
- The first segment of the inheritance (`module`) indicates the directory in which the target overlays are located.
- The inheritance format and scope rules ensure that overlays are correctly resolved based on the file and directory structure.


## 5. Scope and Inheritance Resolution

### 5.1 Scope Definition

In the Overlay language, scope determines the visibility and inheritance relationships of overlays and properties within the current context. The scope structure includes sibling overlays, parent overlays, directory scope, and cross-file inheritance.

**Scope in the Overlay language consists of the following levels**:

- **Sibling Overlays**: The names of other overlays in the same file are visible in the current scope and can be inherited using the format `[overlay_name]`. Inheritance from sibling overlays takes precedence over parent overlay inheritance.

- **Parent Overlays**: The names of all parent overlays in the current hierarchy are visible in the current scope. Resolution starts from the parent scope (not the overlay itself), so an overlay's own name is not directly in its own lookup scope. Additionally, **same-name skip semantics** apply: when an overlay references a name that matches its own key, the first match found during the upward traversal is skipped. This allows an overlay to reference an outer overlay with the same name without creating a self-reference. For example, if `Inner.value` references `[value]`, the algorithm skips the first `value` it finds (which would be `Inner.value` seen from its parent) and resolves to an outer `value` instead. See Section 5.2.1 for the full resolution algorithm.

- **Directory Scope**: A directory has a lexical scope that includes all overlays defined directly within that directory. Files within the directory can inherit overlays in the directory's scope using the format `[directory_name, overlay_name]`.

- **Cross-File Inheritance**: When inheriting overlays across different directories, the path must include the relative path from the current file to the target overlay.

The Overlay language does not distinguish between types and values. Any overlay can represent either a data value or a type. However, in practice, type-like overlays are usually named using the UpperCamelCase convention and represent structures or behaviors to be inherited. Value-like overlays are named using lowercase letters with underscores and typically represent individual values or instances.

### 5.2 Inheritance Resolution

Inheritances in the Overlay language are resolved **dynamically at the time of overlay evaluation or inheritance**. The first segment of the inheritance determines how the target is identified based on the current context.

#### 5.2.1 First Segment Resolution

- **First Segment is an Outer Overlay**: If the first segment inherits an outer overlay (e.g., `[Outer, sibling]`), it behaves like `Outer.this.sibling` in Java, meaning it explicitly inherits the `sibling` property of the `Outer` overlay. This is useful when you want to access an overlay defined in an enclosing scope.

- **First Segment is a Sibling Overlay**: If the first segment inherits a sibling overlay (e.g., `[sibling, sibling_property]`), it behaves like `this.sibling.sibling_property` in Java, meaning it inherits the `sibling` overlay in the current context and then accesses `sibling_property`. This allows you to inherit overlays defined alongside the current overlay.

- **First Segment Resolution in Lexical Scope**:

  - The first segment of the inheritance searches for the overlay name in the current lexical scope, which includes:

    - **Current File**: Overlays defined within the same file.

    - **Parent Overlays**: Overlays in the parent scope of the current overlay.

    - **Directory Scope**: Overlays defined directly within the current directory.

  - **No Inheritance Lookup in First Segment**: The first segment does not search for properties within inherited overlays. To reference inherited members, use qualified this syntax: `[ScopeName, ~, inherited_member]`.

- **Same-Name Skip Semantics**:

  Lexical references implement **same-name skip semantics** (analogous to pytest fixture shadowing). When the first segment of a reference path matches the defining overlay's own key, the first match encountered during the upward scope traversal is skipped, and resolution continues to the next outer scope.

  **Algorithm**:

  1. Let `first_segment` be the first element of the reference path.
  2. If `first_segment` equals the current overlay's key, set `skip_first = true`.
  3. Starting from the parent scope (not the overlay itself), traverse upward through enclosing scopes:
     a. At each scope, check if `first_segment` is an **own property** (not inherited) of that scope.
     b. If found and `skip_first` is `true`: set `skip_first = false` and continue to the next outer scope.
     c. If found and `skip_first` is `false`: resolve the reference to this scope.
     d. If not found: continue to the next outer scope.
  4. If the root is reached without a match, raise a lookup error.

  **Example — single level**:

  ```yaml
  Root:
    value: 10
    Inner:
      value:
        - [value]    # References Root.value (10), not Inner.value itself
        - # ... computes value + 1, resulting in 11
  ```

  Here, `Inner.value` references `[value]`. Because `first_segment` (`value`) matches `Inner`'s own key (`value`), the algorithm skips the first match (the `value` property found in `Root` that corresponds to `Inner.value`'s sibling) and resolves to `Root.value` instead.

  **Example — multiple levels**:

  ```yaml
  Root:
    value: 10
    Level1:
      value:
        - [value]    # Skips Level1.value, resolves to Root.value (10) → 11
      Level2:
        value:
          - [value]  # Skips Level2.value, resolves to Level1.value (11) → 12
  ```

  At each nesting level, the same-name skip ensures that `[value]` resolves to the nearest outer `value`, not to the overlay being defined. This enables recursive-like compositional patterns where each level wraps the value from the level above.

#### 5.2.2 Subsequent Segment Resolution

After resolving the first segment, subsequent segments can access properties within the inherited overlay hierarchy.

- **Inherited Properties**: Subsequent segments can access properties inherited from parent overlays.

- **Dynamic Resolution**: Inheritances are resolved dynamically, meaning that if inherited overlays are extended or overridden in the current context, the inheritance reflects these changes.

#### 5.2.3 Inheritance Resolution Example

Consider the following example:

```yaml
OuterOverlay:
  inner_overlay:
    property: "value"

CurrentOverlay:
  - [OuterOverlay]
  - inheriting_inner:
      - [OuterOverlay, inner_overlay]  # Early binding to 'inner_overlay' in 'OuterOverlay'
  - inheriting_sibling:
      - [sibling_overlay, property]  # Late binding to 'property' in 'sibling_overlay'
  sibling_overlay:
    property: "sibling value"
```

In this example:

- **`inheriting_inner`** inherits `[OuterOverlay, inner_overlay]`:

  - **First Segment**: `OuterOverlay`, which is an outer overlay in the current scope.

  - **Resolution**: It behaves like `OuterOverlay.this.inner_overlay`, inheriting the `inner_overlay` defined in `OuterOverlay`.

- **`inheriting_sibling`** inherits `[sibling_overlay, property]`:

  - **First Segment**: `sibling_overlay`, which is a sibling overlay defined in the same file.

  - **Resolution**: It behaves like `this.sibling_overlay.property`, inheriting the `property` in `sibling_overlay`.

#### 5.2.4 Qualified This Syntax

When a reference needs to access the dynamic `self` of an enclosing overlay (analogous to `Outer.this` in Java), the Overlay language provides an explicit **qualified this** syntax:

```yaml
- [OuterOverlay, ~, property, path]
```

This is an array where the first element is a string (the `selfName` of an enclosing scope), the second element is `null` (written as `~` in YAML), and the remaining elements are strings (the path to navigate within that scope's dynamic `self`). This is analogous to Java's `Outer.this.property.path`.

**Semantics**: The evaluator walks the symbol table chain to find a scope whose `selfName` matches the first element, retrieves that scope's dynamic `self` (the fully composed evaluation), and then navigates the path segments through `allProperties`.

**Example**:

```yaml
NatAdd:
  - [types, Nat]                    # Inheritance (all-string array)
  - augend:
      - [types, Nat]
    addend:
      - [types, Nat]
    _applied_addend:
      - [NatAdd, ~, addend]         # Qualified this: NatAdd.self.addend
      - successor:
          - [NatAdd, ~, successor]  # Qualified this: NatAdd.self.successor
        zero:
          - [NatAdd, ~, zero]       # Qualified this: NatAdd.self.zero
    result:
      - [_applied_addend, result]   # Regular variable reference (not qualified this)
```

In this example, `[NatAdd, ~, successor]` accesses `successor` through NatAdd's dynamic `self`. This is necessary because `successor` is inherited from `Nat` and not directly accessible as a lexical variable within `_applied_addend`'s scope (where `successor` is shadowed by `_applied_addend`'s own property).

**When to use qualified this vs. direct references**:

- Use a direct reference `[property]` or `[property, subproperty]` when the first segment is accessible in the current lexical scope (as an own property or via outer scopes).
- Use qualified this `[SelfName, ~, property, path]` when the property is only accessible through the dynamic `self` of an enclosing overlay (e.g., inherited properties that are shadowed in the current scope).

**Distinction from inheritance references**: An inheritance reference is an all-string array like `[types, Nat]`. A qualified this reference contains a `null` delimiter after the self name: `[NatAdd, ~, successor]`. The evaluator distinguishes between these based on whether the second element is `null`.

#### 5.2.5 Cross-Directory Inheritance

When inheriting overlays across different directories, the path must include relative path segments:

```yaml
- [path, to, overlay_name, property]
```

- **First Segment**: `path` is interpreted relative to the directory structure of the current file.

- **Resolution**: the Overlay language will automatically search for the inherited overlay by traversing the directory hierarchy.

### 5.3 Multiple Inheritance and Scalar Value Handling

the Overlay language supports **conflict-free multiple inheritance**, allowing overlays to inherit properties and scalar values from multiple parent overlays without conflicts. This feature enables the flexible composition of complex structures by combining the functionalities of various overlays.

#### 5.3.1 Inheritance and Property Merging

When an overlay inherits from multiple parent overlays, the properties from all parents are **merged** into the child overlay. If multiple parent overlays define the same property, the definitions are automatically combined, avoiding naming conflicts and preserving all inherited behaviors.

**Example:**

```yaml
# basic_features.oyaml
Vehicle:
  - wheels: [Number]
  - engine: {}

Motor:
  - engine:
      gasoline: true # Scalar value for 'engine'

# advanced_features.oyaml
hybrid_car:
  - ["basic_features", Vehicle]
  - ["basic_features", Motor]
  - wheels: 4 # Scalar value for 'wheels'
  - engine: # Merging with 'Vehicle.engine'
      hybrid: true
  - battery_capacity: 100 # New property
```

In this example:

- **Inheritance**:
  - `hybrid_car` inherits from both `Vehicle` and `Motor`.
- **Property Merging**:
  - The `engine` property is defined in both parent overlays.
  - the Overlay language automatically merges the `engine` property without conflict.
- **Resulting Properties**:
  - `hybrid_car` has access to all properties from both parents: `wheels`, `engine`, and `battery_capacity`.

#### 5.3.2 Scalar Value Merging

Scalar values (e.g., strings, numbers, booleans) can coexist with properties within an overlay and can be inherited from multiple parent overlays. the Overlay language does not define specific rules for merging scalar values from different parents; instead, scalar values from all parents are included in the child overlay without causing errors. The **specific merging behavior** of scalar values is defined by the libraries used in conjunction with the Overlay language, allowing for different strategies depending on the application's needs.

**Example:**

```yaml
# number.oyaml
Number:
  - {} # Represents a number type overlay

# value.oyaml
value_42:
  - 42 # Defines scalar value 42

# my_number.oyaml
my_number:
  - [Number]
  - [value_42]
```

In this example:

- **Inheritance**:
  - `my_number` inherits from both `Number` and `value_42`.
- **Scalar Value Coexistence**:
  - Combines the scalar value `42` and any properties from `Number`.
- **No Conflict**:
  - Scalar values and properties coexist without conflict in `my_number`.

#### 5.3.3 Merging Scalar Values with Properties

An overlay can have both scalar values and properties, and these can be inherited from multiple parents. the Overlay language allows this combination without conflicts, enabling more expressive and flexible overlay definitions.

**Example:**

```yaml
# person.oyaml
PersonDetails:
  name: [String]
  age: [Number]

# height.oyaml
height_value: 180 # Scalar value representing height

# combined_person.oyaml
combined_person:
  - [PersonDetails]
  - name: "John Doe"
  - age: 30
  - [height_value]
```

In this example:

- **Inheritance**:
  - `combined_person` inherits from both `PersonDetails` and `height_value`.
- **Combined Properties and Scalar Values**:
  - Includes properties `name` and `age`, and scalar value `180`.
- **No Conflict**:
  - Both properties and scalar values are accessible without conflict.

#### 5.3.4 Conflict-Free Inheritance

the Overlay language's approach to inheritance ensures that properties and scalar values from multiple parents are merged seamlessly. This conflict-free inheritance model eliminates issues commonly associated with multiple inheritance in other languages, such as the diamond problem.

- **Automatic Merging**: Properties with the same name are automatically merged.
- **No Overwriting**: Scalar values and properties from different parents do not overwrite each other unless explicitly redefined in the child overlay.
- **Flexibility**: Developers can compose overlays freely without worrying about inheritance conflicts.

**Example of Conflict-Free Inheritance:**

```yaml
# basic_features.oyaml
Vehicle:
  - wheels: [Number]
  - engine:
      gasoline: true # Scalar value for 'engine'

Motor:
  - engine: {} # Defines 'engine' property

# advanced_features.oyaml
hybrid_car:
  - ["basic_features", Vehicle]
  - ["basic_features", Motor]
  - wheels: 4 # Scalar value for 'wheels'
  - engine: # Merging with 'Vehicle.engine'
      hybrid: true
  - battery_capacity: 100 # New property
```

In this example:

- **Inheritance**:
  - `hybrid_car` inherits from both `Vehicle` and `Motor`.
- **Property Merging**:
  - Merges `engine` properties from parents.
- **Resulting Properties**:
  - Combines properties `wheels`, `engine`, and `battery_capacity` in `hybrid_car`.

## 6. Binding Rules and Examples

Inheritances in the Overlay language can be resolved using either **early binding** or **late binding** mechanisms. Understanding these binding rules is crucial for determining how overlays and properties are inherited and resolved during evaluation. The following example illustrates the differences between early and late binding within a single overlay structure.

### 6.1 Example

Consider the following the Overlay language definition:

```yaml
test_binding:
  my_overlay1:
    - inner:
        field1: "value1"
    - early_binding:
        - [test_binding, ~, my_overlay1, inner] # Early binding to 'inner' in 'my_overlay1'
    - late_binding:
        - [my_overlay1, ~, inner] # Late binding to 'inner' in 'my_overlay1'
    - late_binding_too:
        - [inner] # Late binding within the same overlay

  my_overlay2:
    - [my_overlay1]
    - inner:
        field2: "value2"
```

### 6.2 Explanation of Binding Mechanisms

#### 6.2.1 Early Binding

- **Definition**: Early binding resolves inheritances at the time of overlay definition. The inheritance remains fixed and does not change even if the overlay is inherited or extended in different contexts.

- **Behavior in Example**:

  - `test_binding.my_overlay1.early_binding` inherits `[test_binding, my_overlay1, inner]`. This means it always points to the original `inner` overlay defined within `my_overlay1`, regardless of how `my_overlay1` is inherited or extended.

- **Result**:

  - `test_binding.my_overlay2.early_binding` contains only `field1` because it inherits the original `my_overlay1.inner`, which has only `field1`. It does not adapt to the additional `field2` added in `my_overlay2.inner`.

#### 6.2.2 Late Binding

- **Definition**: Late binding resolves inheritances dynamically at the time of overlay evaluation or inheritance. The inheritance adapts to the current context, including any changes made through inheritance or property merging.

- **Behavior in Example**:

  - `test_binding.my_overlay1.late_binding` inherits `[my_overlay1, ~, inner]`. When inherited by `my_overlay2`, this inheritance dynamically resolves to `my_overlay2.inner`, which includes both `field1` and `field2`.

  - Similarly, `test_binding.my_overlay1.late_binding_too` inherits `[inner]` within the same overlay. When inherited by `my_overlay2`, it also resolves to `my_overlay2.inner`, which now contains both `field1` and `field2`.

- **Result**:

  - Both `test_binding.my_overlay2.late_binding` and `test_binding.my_overlay2.late_binding_too` contain both `field1` and `field2`, as the late-bound inheritances adapt to the current context of `my_overlay2.inner`.

### 6.2.3 Key Observations

1. **Early Binding**:

   - **Fixed Inheritance**: Always points to the originally defined overlay or property.
   - **Example Behavior**: `test_binding.my_overlay2.early_binding` only includes `field1` because it inherits the original `my_overlay1.inner` and does not adapt to changes in `my_overlay2`.

2. **Late Binding**:

   - **Dynamic Inheritance**: Adapts to the current overlay context, including any inherited or merged properties.
   - **Example Behavior**: Both `test_binding.my_overlay2.late_binding` and `test_binding.my_overlay2.late_binding_too` include both `field1` and `field2` because they inherit `my_overlay2.inner`, which dynamically includes all fields.

3. **The First Segment Determines the Resolution Method**:

   - If the first segment inherits an outer overlay (e.g., `[test_binding, my_overlay1, inner]`), it uses early binding, behaving like an explicit inheritance to a specific overlay.
   - If the first segment inherits a sibling overlay or the current context (e.g., `[my_overlay1, inner]` or `[inner]`), it uses late binding and is dynamically resolved based on the current overlay's inheritance and context.

### 6.3 Practical Guidelines

To effectively use early and late binding in the Overlay language:

- **Use Early Binding When**:

  - You need an inheritance to always point to a specific overlay or property, regardless of how the overlay is inherited or extended.
  - You want to ensure that a property remains constant and unaffected by changes in the inheritance hierarchy.

- **Use Late Binding When**:
  - You want inheritances to adapt dynamically based on the context in which the overlay is used.
  - You are building overlays intended for reuse and extension, where properties may be added or merged.

### 6.4 Summary

In the Overlay language, choosing between early and late binding allows you to control how inheritances are resolved during inheritance and evaluation:

- **Early Binding**: Ensures a fixed inheritance that remains constant across all contexts.
- **Late Binding**: Provides flexibility by adapting to the current context, making it suitable for dynamic and extensible overlay definitions.

By understanding these binding rules and how the first segment of an inheritance determines the resolution mechanism, you can design overlays that behave predictably and flexibly, depending on your use case.

## 7. Appendices

This section provides additional resources and references to aid in the understanding of the Overlay language. It includes a JSON Schema reference, which defines the structure of Overlay files, and a glossary of terms used throughout the language specification.

### 7.1 JSON Schema Reference

The JSON Schema that defines the structure of Overlay files is maintained in [`mixin.schema.json`](mixin.schema.json). It specifies the types and constraints for overlay definitions, including inheritances, qualified `this` references, properties, and inheritance rules. This schema is useful for validating Overlay files to ensure they conform to the expected format.

#### Explanation of the Schema

- **Inheritance**:

  - Represents an inheritance to another overlay or module. Defined as an array of strings. This format is used to point to other overlays within the same file or across files.
  - Example: `[module_name, overlay_name]` or `[file_name, overlay_name]`.

- **Properties**:

  - Represents a collection of property definitions within an overlay. Each property can be another overlay or a scalar value (string, number, boolean, or null).
  - Example:
    ```yaml
    person:
      name: "John Doe"
      age: 30
      is_employed: true
    ```

- **Inheritance and Own Properties**:

  - Represents a combination of inheritance and property definitions within an overlay. This allows an overlay to inherit from other overlays while also defining its own properties.
  - Example:
    ```yaml
    Car:
      - [Vehicle]
      - model: "Sedan"
      - color: "Blue"
    ```

- **Overlay**:

  - Represents an overlay definition. An overlay can be an inheritance to another overlay, a set of properties, or a combination of inheritance and properties.

This schema provides a structured way to define and validate overlays in the Overlay language, ensuring consistency and correct syntax across different files and formats.

### 7.2 Glossary

This section provides definitions of key terms used in the Overlay language specification.

- **Overlay**: The fundamental building block in the Overlay language. It represents a reusable unit that can contain properties, inheritances, or scalar values. Overlays can be inherited, composed, and combined to form complex data structures and logic.

- **Inheritance**: A mechanism for pointing to another overlay or module. An inheritance is represented as an array of strings, indicating the path to the target overlay. Inheritance in the Overlay language is conflict-free, allowing multiple parent overlays to be combined without error.

- **Property**: A named value within an overlay. Properties are named overlays, containing scalar values (e.g., strings, numbers), inheritances to other overlays, or nested properties. Properties define the internal structure or behavior of an overlay.

- **Scalar Value**: A single, indivisible value within an overlay, such as a string, number, boolean, or null. Scalar values can be merged with other properties in an overlay.

- **Early Binding**: A type of inheritance resolution where the inheritance is resolved at the time of overlay definition. The inheritance remains fixed, regardless of changes in inheritance or context.

- **Late Binding**: A type of inheritance resolution where the inheritance is dynamically resolved at the time of overlay evaluation or inheritance. This allows inheritances to adapt to changes in the inheritance hierarchy.

- **Lexical Scope**: The context in which an overlay or property is defined. The lexical scope determines the visibility of overlays and properties within a file, directory, or project.

- **Same-Name Skip Semantics**: A lexical reference resolution rule that prevents self-reference. When the first segment of a reference path matches the defining overlay's own key, the first match found during the upward scope traversal is skipped. This allows an overlay to naturally reference an outer overlay with the same name, similar to how pytest fixtures shadow outer fixtures of the same name. See Section 5.2.1 for details.

- **Directory Scope**: The scope defined by a directory. All overlays within a directory are part of the directory scope, and files within the directory can inherit overlays using the directory scope.

- **Cross-File Inheritance**: An inheritance that points to an overlay defined in a different file. The inheritance format includes the file name and overlay name, and the Overlay language will automatically search for the target overlay within the directory hierarchy.

- **Schema**: A JSON Schema definition that describes the structure of an Overlay file. The schema defines the types, constraints, and relationships between overlays, properties, and inheritances.

- **File Format**: The supported formats for defining the Overlay language source code. the Overlay language supports YAML, JSON, and TOML, with restrictions to ensure compatibility with JSON serialization.

- **Naming Convention**: The rules for naming overlays and files in the Overlay language. These conventions help distinguish between type-like overlays, value-like overlays, and instances, and ensure clarity and consistency in code organization.

- **Conflict-Free Inheritance**: the Overlay language's approach to inheritance ensures that properties and scalar values from multiple parents are merged seamlessly without conflicts. This model eliminates issues commonly associated with multiple inheritance in other languages, such as the diamond problem.

- **Property Merging**: The process by which properties with the same name from multiple parent overlays are automatically combined into the child overlay without causing conflicts.

- **Inheritance Hierarchy**: The structure formed by overlays inheriting from other overlays, creating a tree-like or graph-like relationship that defines how properties and inheritances are propagated.
