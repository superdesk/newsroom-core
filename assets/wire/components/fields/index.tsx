import React from 'react';
import {Source} from './Source';
import {UrgencyLabel} from './UrgencyLabel';
import {DurationLabel} from './DurationLabel';
import {CharCount} from './CharCount';
import {WordCount} from './WordCount';
import {PreviousVersions} from './PreviousVersions';
import {Embargo} from './Embargo';
import {VersionCreated} from './VersionCreated';
import {VersionType} from './VersionType';
import {ExpiryDateLabel} from './ExpiryDateLabel';
import {
    IDisplayFieldsConfig as FieldConfig,
    Separator,
    StyledField,
    ComponentField,
    FieldRenderComponent,
    FieldRenderProps
} from 'interfaces/configs';
import {IArticle} from 'interfaces';


interface FieldResult {
    key: string;
    Component: FieldRenderComponent;
}

interface FieldComponentsProps {
    config: FieldConfig;
    item: IArticle;
    fieldProps?: FieldRenderProps;
}

const ALLOWED_SEPARATORS: Array<Separator> = ['/', '//', '-'];

const SEPARATOR_KEY = 'separator';

const isSeparator = (f: FieldConfig): f is Separator =>
    typeof f === 'string' && (ALLOWED_SEPARATORS).includes(f as Separator);

const isStringField = (f: FieldConfig): f is keyof IArticle => typeof f === 'string' && !isSeparator(f);

const isObjectCfg = (f: FieldConfig): f is StyledField | ComponentField =>
    typeof f === 'object' && f !== null && !Array.isArray(f);

const isStyledField = (f: FieldConfig): f is StyledField => isObjectCfg(f) && 'styles' in f;

const isComponentField = (f: FieldConfig): f is ComponentField => isObjectCfg(f) && 'component' in f;

const MAP_FIELD_TO_COMPONENT = {
    urgency: UrgencyLabel,
    source: Source,
    duration: DurationLabel,
    charcount: CharCount,
    wordcount: WordCount,
    previous_versions: PreviousVersions,
    embargo: Embargo,
    versioncreated: VersionCreated,
    expiry: ExpiryDateLabel,
};

/**
 * Example config:
 * [
 *   "urgency", // simple field
 *   ["charcount", "/", "wordcount"], // multiple fields on the same line
 *   ["source", "//", {field: "department", styles: {fontWeight: "bold"}}] // custom styles
 * ]
 */
export function FieldComponents({config, item, fieldProps = {}}: FieldComponentsProps) {
    if (!Array.isArray(config)) {
        return null;
    }

    const fields = config
        .map((field) => getComponentForField(item, field))
        .filter(x => x !== null)
        .reduce((acc, curr) => {
            if (acc.length > 0 && acc[acc.length - 1].key === curr.key) {
                // remove adjacent separators
                return acc;
            }
            return [...acc, curr];
        }, [] as Array<FieldResult>);

    let separator = 0;

    const components = fields.map(({key, Component}: FieldResult) => {
        const _key =
            key === SEPARATOR_KEY ? `${SEPARATOR_KEY}${++separator}` : key;

        return (
            <span className="meta-info-block" key={_key}>
                <Component item={item} {...fieldProps} />
            </span>
        );
    });

    return <>{components}</>;
}

/**
 * Recursively resolves a field configuration into a FieldResult containing a React component and a unique key.
 *
 * Handles arrays (composite fields), separators, styled fields, component overrides, and string fields.
 *
 * @param item - The article data object to extract field values from.
 * @param fieldConfig - The field configuration describing what to render.
 * @returns A FieldResult with a key and a React component, or null if the config is invalid or not renderable.
 */
function getComponentForField(item: IArticle, fieldConfig: FieldConfig): FieldResult | null {
    if (Array.isArray(fieldConfig) && fieldConfig.length > 0) {
        // example: ["source", "//", "department"]
        const components = fieldConfig
            .map((f: any) => getComponentForField(item, f))
            .filter(x => x !== null);

        // remove orphan separators. For example in ['source', '//', 'department']
        // if the 'department' is empty, then '//' should not be shown
        if (components[components.length - 1].key === SEPARATOR_KEY) {
            components.pop();
        }

        return {
            key: components.map(({key}) => key).join('-'),
            Component: (props: any) => (
                <span>
                    {components.map(({Component}, i) => (
                        <Component key={i} {...props} />
                    ))}
                </span>
            ),
        };
    }

    if (isSeparator(fieldConfig)) {
        return {
            key: SEPARATOR_KEY, // will be modified afterwards, as it's not unique
            Component: () => <span> {fieldConfig} </span>,
        };
    }

    if (isStyledField(fieldConfig)) {
        // example: { field: "source", styles: {fontWeight: "bold"} }
        const inner = getComponentForField(item, fieldConfig.field);

        if (!inner) return null;

        return {
            key: fieldConfig.field as string,
            Component: (props: any) => (
                <span style={fieldConfig.styles || {}}>
                    <inner.Component {...props} />
                </span>
            ),
        };
    }

    if (isComponentField(fieldConfig)) {
        // example: { field: "version", component: "version_type" }
        switch (fieldConfig.component) {
        case 'version_type':
            return {
                key: fieldConfig.field,
                Component: () => (
                    <VersionType value={item[fieldConfig.field] as string} />
                ),
            };
        }

        return null;
    }

    if (isStringField(fieldConfig)) {
        let Component = null;

        // example: "source"
        if (fieldConfig in MAP_FIELD_TO_COMPONENT) {
            // predefined component
            const fieldKey = fieldConfig as keyof typeof MAP_FIELD_TO_COMPONENT;
            Component = MAP_FIELD_TO_COMPONENT[fieldKey];
        } else if (typeof item[fieldConfig] === 'string') {
            // string value from item
            Component = () => <span className="test">{item[fieldConfig]}</span>;
        }

        if (Component) {
            return {
                key: fieldConfig,
                Component: Component as FieldRenderComponent,
            };
        }

        return null;
    }

    console.warn(`Unknown field format ${fieldConfig}`);

    return null;
}
