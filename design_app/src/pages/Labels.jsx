import React from 'react';

import {Label} from 'components/Label';
import TopStoryLabel from 'agenda/components/TopStoryLabel';
import ToBeConfirmedLabel from 'agenda/components/ToBeConfirmedLabel';
import AgendaListItemLabels from 'agenda/components/AgendaListItemLabels';
import {CoverageUpdateComing} from 'agenda/components/preview/coverage/CoverageUpdateComing';
import WireLabel from 'wire/components/WireLabel';
import {UrgencyLabel} from 'wire/components/fields/UrgencyLabel';
import {MatchLabel} from 'wire/components/fields/MatchLabel';
import {Embargo} from 'wire/components/fields/Embargo';
import {getUserStateLabelDetails} from 'company-admin/components/CompanyUserListItem';

// The design app has no server config; TopStoryLabel and WireLabel read their subject schemes from it.
const TOP_STORY_SCHEME = 'design-top-story';
const WIRE_LABELS_SCHEME = 'design-wire-labels';

window.newsroom = window.newsroom || {};
window.newsroom.client_config = {
    agenda_top_story_scheme: TOP_STORY_SCHEME,
    wire_labels_scheme: WIRE_LABELS_SCHEME,
    ...window.newsroom.client_config,
};

// Palette keys of $label-colors in assets/styles/labels.scss (the semantic keys are covered by <Label>)
const PALETTE = [
    'top-story', 'blue', 'green', 'green-dark', 'orange', 'orange2', 'red',
    'available', 'restricted', 'yellow', 'gray-dark', 'gray-mid',
];

const LABEL_TYPES = [undefined, 'success', 'warning', 'alert', 'info', 'highlight'];
const LABEL_STYLES = ['fill', 'hollow', 'translucent'];
const LABEL_SIZES = ['small', 'medium', 'big'];

const topStoryItem = {subject: [{name: 'Top Story', code: 'top', scheme: TOP_STORY_SCHEME}]};
const toBeConfirmedItem = {event: {occur_status: {qcode: 'eocstat:eos3'}}};
const wireLabelItem = {
    subject: ['latest', 'alert', 'advisory', 'press-release'].map((code) => ({
        name: code, code: code, scheme: WIRE_LABELS_SCHEME,
    })),
};
// The shipped defaults from newsroom/init_data/ui_config.json (wire.list.highlights.urgency).
// Only two colours, so urgency 3 and above get no colour and the label renders nothing.
const urgencyListConfig = {highlights: {urgency: ['#C20000', '#AF821A']}};
// More than 48h ahead, so Embargo does not schedule its "lifted" re-render.
const embargoedItem = {embargoed: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()};
const updatingCoverage = {deliveries: [{delivery_state: 'in_progress'}]};
const userStates = [
    {is_approved: true, is_enabled: true, is_validated: true},
    {is_approved: false, is_enabled: true, is_validated: false},
    {is_approved: true, is_enabled: false, is_validated: true},
];

function Section({title, source, note, children}) {
    return (
        <section className="mb-5">
            <h3 className="mb-1">{title}</h3>
            <p className="mb-3">
                <code>{source}</code>
                {note && <span className="ms-2 text-muted">{note}</span>}
            </p>
            {children}
        </section>
    );
}

function Example({caption, children}) {
    return (
        <div className="d-flex align-items-center gap-3 mb-2 flex-wrap">
            <div style={{minWidth: '18rem'}}>
                <code>{caption}</code>
            </div>
            <div className="d-flex align-items-center gap-2 flex-wrap">{children}</div>
        </div>
    );
}

function Labels() {
    return (
        <div className="p-4" style={{overflowY: 'auto', width: '100%'}}>
            <h2 className="mb-4">Labels</h2>

            <Section
                title="<Label>"
                source="assets/components/Label.tsx"
                note={<>Always adds <code>label--rounded</code>. Does not support palette colours.</>}
            >
                {LABEL_STYLES.map((style) => (
                    <Example key={style} caption={`style="${style}"`}>
                        {LABEL_TYPES.map((type) => (
                            <Label key={type || 'default'} text={type || 'default'} type={type} style={style} />
                        ))}
                    </Example>
                ))}
                {LABEL_SIZES.map((size) => (
                    <Example key={size} caption={`size="${size}"`}>
                        {LABEL_TYPES.map((type) => (
                            <Label key={type || 'default'} text={type || 'default'} type={type} size={size} />
                        ))}
                    </Example>
                ))}
            </Section>

            <Section
                title="Palette classes (raw markup)"
                source="assets/styles/labels.scss — $label-colors"
                note={<>Used directly by the components below and by newsroom/templates/design_*.html.
                    Translucent text is darkened to OKLCH lightness ≤ 0.45 for WCAG AA contrast.</>}
            >
                <Example caption=".label.label--{name}">
                    {PALETTE.map((name) => (
                        <span key={name} className={`label label--${name}`}>{name}</span>
                    ))}
                </Example>
                <Example caption=".label.label--rounded.label--{name}">
                    {PALETTE.map((name) => (
                        <span key={name} className={`label label--rounded label--${name}`}>{name}</span>
                    ))}
                </Example>
                <Example caption=".label.label--big.label--rounded.label--{name}">
                    {PALETTE.map((name) => (
                        <span key={name} className={`label label--big label--rounded label--${name}`}>{name}</span>
                    ))}
                </Example>
                <Example caption=".label.label--rounded.label--hollow.label--{name}">
                    {PALETTE.map((name) => (
                        <span key={name} className={`label label--rounded label--hollow label--${name}`}>{name}</span>
                    ))}
                </Example>
                <Example caption=".label.label--rounded.label--translucent.label--{name}">
                    {PALETTE.map((name) => (
                        <span key={name} className={`label label--rounded label--translucent label--${name}`}>{name}</span>
                    ))}
                </Example>
            </Section>

            <Section title="<TopStoryLabel>" source="assets/agenda/components/TopStoryLabel.tsx">
                <Example caption="size default">
                    <TopStoryLabel item={topStoryItem} config={{}} />
                </Example>
                <Example caption='size="big"'>
                    <TopStoryLabel item={topStoryItem} config={{}} size="big" />
                </Example>
            </Section>

            <Section title="<ToBeConfirmedLabel>" source="assets/agenda/components/ToBeConfirmedLabel.tsx">
                <Example caption="size default">
                    <ToBeConfirmedLabel item={toBeConfirmedItem} />
                </Example>
                <Example caption='size="big"'>
                    <ToBeConfirmedLabel item={toBeConfirmedItem} size="big" />
                </Example>
            </Section>

            <Section title="<AgendaListItemLabels>" source="assets/agenda/components/AgendaListItemLabels.tsx">
                <Example caption="state: postponed / cancelled / rescheduled / completed">
                    <AgendaListItemLabels item={{state: 'postponed'}} />
                    <AgendaListItemLabels item={{state: 'cancelled'}} />
                    <AgendaListItemLabels item={{state: 'rescheduled'}} />
                    <AgendaListItemLabels item={{event: {completed: true}}} />
                </Example>
            </Section>

            <Section
                title="<CoverageUpdateComing>"
                source="assets/agenda/components/preview/coverage/CoverageUpdateComing.tsx"
            >
                <Example caption="delivery in progress">
                    <CoverageUpdateComing coverage={updatingCoverage} />
                </Example>
            </Section>

            <Section
                title="Subject labels (raw markup)"
                source="assets/agenda/components/AgendaListItemIcons.tsx"
                note={<>No <code>subject--*</code> styles are defined.</>}
            >
                <Example caption=".label.label--rounded.subject--{qcode}">
                    <span className="label label--rounded subject--01000000">Arts</span>
                    <span className="label label--rounded subject--15000000">Sport</span>
                </Example>
            </Section>

            <Section title="<WireLabel>" source="assets/wire/components/WireLabel.tsx">
                <Example caption=".label--fill.label--rounded.label-wire--{code}">
                    <WireLabel item={wireLabelItem} />
                </Example>
            </Section>

            <Section
                title="<UrgencyLabel>"
                source="assets/wire/components/fields/UrgencyLabel.tsx"
                note={<>Colours come from <code>listConfig.highlights.urgency</code> as inline styles: the text
                    is the colour itself and the background that colour at 8.24% via <code>color-mix()</code>.
                    The element carries no palette class.</>}
            >
                <Example caption="urgency 1 / 2 (shipped defaults: #C20000, #AF821A)">
                    {[1, 2].map((urgency) => (
                        <UrgencyLabel key={urgency} item={{urgency}} listConfig={urgencyListConfig} />
                    ))}
                </Example>
                <Example caption="urgency 3: no colour configured — renders nothing">
                    <UrgencyLabel item={{urgency: 3}} listConfig={urgencyListConfig} />
                </Example>
                <Example caption='urgency 3 with alwaysShow: plain text, no label classes'>
                    <UrgencyLabel item={{urgency: 3}} listConfig={urgencyListConfig} alwaysShow />
                </Example>
                <Example caption='filterGroupLabels={{urgency: "Urgency"}}'>
                    <UrgencyLabel item={{urgency: 1}} listConfig={urgencyListConfig} filterGroupLabels={{urgency: 'Urgency'}} />
                </Example>
            </Section>

            <Section title="<MatchLabel>" source="assets/wire/components/fields/MatchLabel.tsx">
                <Example caption="default">
                    <MatchLabel />
                </Example>
            </Section>

            <Section
                title="Versions button (raw markup)"
                source="assets/wire/components/WireListItem.tsx"
            >
                <Example caption="with matches / without matches">
                    <button className="label label--rounded label--green">2 versions</button>
                    <button className="label label--rounded label--green bg-transparent text-primary">2 versions</button>
                </Example>
            </Section>

            <Section
                title="<Embargo>"
                source="assets/wire/components/fields/Embargo.tsx"
                note={<>The lifted state (<code>label--available</code>) only renders after the embargo passes; shown as markup.</>}
            >
                <Example caption="embargoed / lifted">
                    <Embargo item={embargoedItem} />
                    <span className="label label--available">embargo</span>
                </Example>
            </Section>

            <Section
                title="User state labels (raw markup)"
                source="assets/company-admin/components/CompanyUserListItem.tsx, assets/users/components/EditUser.tsx"
                note="Colour from getUserStateLabelDetails()."
            >
                <Example caption="CompanyUserListItem: label--rounded label--translucent">
                    {userStates.map((user, i) => {
                        const details = getUserStateLabelDetails(user);

                        return (
                            <label key={i} className={`label label--${details.colour} label--rounded label--translucent`}>
                                {details.text}
                            </label>
                        );
                    })}
                </Example>
                <Example caption="EditUser: label--big label--rounded label--translucent">
                    {userStates.map((user, i) => {
                        const details = getUserStateLabelDetails(user);

                        return (
                            <label key={i} className={`label label--${details.colour} label--big label--rounded label--translucent`}>
                                {details.text}
                            </label>
                        );
                    })}
                </Example>
            </Section>
        </div>
    );
}

export default Labels;
