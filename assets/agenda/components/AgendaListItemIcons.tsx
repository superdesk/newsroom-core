import React from 'react';
import {isEqual} from 'lodash';

import {IAgendaItem, IUser, ICoverage, IListConfig} from 'interfaces';
import {bem} from 'ui/utils';
import {
    hasCoverages,
    isCoverageForExtraDay,
    isRecurring,
    getInternalNote,
    getAttachments,
    getSubjects
} from '../utils';

import AgendaListItemLabels from './AgendaListItemLabels';
import AgendaMetaTime from './AgendaMetaTime';
import AgendaInternalNote from './AgendaInternalNote';
import AgendaListCoverageItem from './AgendaListCoverageItem';
import AgendaLocation from './AgendaLocation';

import {gettext, isDisplayed} from 'utils';
import {AgendaContacs} from './AgendaContacts';

interface IProps {
    user: IUser['_id'];
    group: string;
    item: IAgendaItem;
    planningItem?: IAgendaItem;
    hideCoverages?: boolean;
    row?: boolean;
    isMobilePhone?: boolean;
    listConfig: IListConfig;
}

interface IState {
    internalNote: string;
    coveragesToDisplay: Array<ICoverage>;
    attachments: number;
    isRecurring: boolean;
}

class AgendaListItemIcons extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = this.getUpdatedState();
    }

    itemChanged(nextProps: Readonly<IProps>) {
        return this.props.item._id !== nextProps.item._id ||
            this.props.item._etag !== nextProps.item._etag ||
            !isEqual(this.props.item.coverages, nextProps.item.coverages);
    }

    shouldComponentUpdate(props: Readonly<IProps>) {
        return this.itemChanged(props);
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (this.itemChanged(prevProps)) {
            this.setState(this.getUpdatedState());
        }
    }

    getUpdatedState(): IState {
        return {
            internalNote: getInternalNote(this.props.item, this.props.planningItem),
            coveragesToDisplay: !hasCoverages(this.props.item) || this.props.hideCoverages ?
                [] :
                (this.props.item.coverages || []).filter((c) => (
                    !this.props.group ||
                    c.scheduled == null ||
                    (
                        isCoverageForExtraDay(c, this.props.group) &&
                        (
                            this.props.planningItem == null ||
                            c.planning_id === this.props.planningItem?.guid
                        )
                    )
                )),
            attachments: (getAttachments(this.props.item)).length,
            isRecurring: isRecurring(this.props.item),
        };
    }

    getItemByschema(props: IProps) {
        const {listConfig} = props;
        if (listConfig.subject != null) {
            const scheme = listConfig.subject.scheme;
            const subjects = getSubjects(props.item);
            return scheme == null ?
                subjects :
                subjects.filter((item: any) => Array.isArray(scheme) ?
                    scheme.includes(item.scheme) :
                    item.scheme === scheme
                );
        }
        return [];
    }

    render() {
        const props = this.props;
        const state = this.state;
        const className = bem('wire-articles', 'item__meta', {row: props.row});
        const subject = this.getItemByschema(props);

        return (
            <div className={className}>
                <AgendaMetaTime
                    item={props.item}
                    borderRight={props.isMobilePhone}
                    isRecurring={state.isRecurring}
                    group={props.group}
                    isMobilePhone={props.isMobilePhone}
                />

                {state.coveragesToDisplay.length > 0 && (
                    <div className='wire-articles__item__icons wire-articles__item__icons--dashed-border'>
                        {state.coveragesToDisplay.map((coverage, index) => (
                            <AgendaListCoverageItem
                                key={index}
                                user={props.user}
                                coverage={coverage}
                                showBorder={props.isMobilePhone && index === state.coveragesToDisplay.length - 1}
                                group={props.group}
                                planningItem={props.planningItem}
                            />
                        ))}
                    </div>
                )}

                {subject.length !== 0 && (
                    <div>
                        {subject.map((item: any) => (
                            <span
                                key={item.qcode}
                                className={`label label--rounded subject--${item.qcode}`}
                            >
                                {item.name}
                            </span>
                        ))}
                    </div>
                )}

                {state.attachments > 0 && (
                    <div className='d-flex align-items-center wire-articles__item__icons--dashed-border'>
                        <i className='icon-small--attachment'
                            title={gettext('{{ attachments }} file(s) attached', {attachments: state.attachments})}
                        />
                    </div>
                )}

                <div className='wire-articles__item__meta-info align-items-center'>
                    <AgendaLocation item={props.item} isMobilePhone={props.isMobilePhone} border={state.internalNote} />

                    {isDisplayed('contacts', props.listConfig) && (
                        <AgendaContacs item={props.item} inList={true} />
                    )}

                    {!props.isMobilePhone && (
                        <AgendaInternalNote internalNote={state.internalNote} onlyIcon={true}/>
                    )}

                    <AgendaListItemLabels item={props.item} />
                </div>
            </div>
        );
    }
}

export default AgendaListItemIcons;
