import React from 'react';
import {get, isEqual} from 'lodash';
import {
    hasCoverages,
    isCoverageForExtraDay,
    isRecurring,
    getInternalNote,
    getAttachments,
} from '../utils';

import AgendaListItemLabels from './AgendaListItemLabels';
import AgendaMetaTime from './AgendaMetaTime';
import AgendaInternalNote from './AgendaInternalNote';
import AgendaListCoverageItem from './AgendaListCoverageItem';
import AgendaLocation from './AgendaLocation';
import {bem} from 'assets/ui/utils';
import {gettext} from 'assets/utils';

interface IProps {
    item: any;
    planningItem: any;
    group: string;
    hideCoverages?: boolean;
    row?: boolean;
    isMobilePhone?: boolean;
    user: string;
}

class AgendaListItemIcons extends React.Component<IProps, any> {
    constructor(props: IProps) {
        super(props);

        this.state = this.getUpdatedState(props);
    }

    itemChanged(nextProps: IProps) {
        return get(this.props, 'item._id') !== get(nextProps, 'item._id') ||
            get(this.props, 'item._etag') !== get(nextProps, 'item._etag') ||
            !isEqual(get(this.props, 'item.coverages'), get(nextProps, 'item.coverages'));
    }

    shouldComponentUpdate(nextProps: IProps) {
        return this.itemChanged(nextProps);
    }

    componentWillReceiveProps(nextProps: IProps) {
        if (this.itemChanged(nextProps)) {
            this.setState(this.getUpdatedState(nextProps));
        }
    }

    getUpdatedState(props: IProps) {
        return {
            internalNote: getInternalNote(props.item, props.planningItem),
            coveragesToDisplay: !hasCoverages(props.item) || props.hideCoverages ?
                [] :
                (props.item.coverages || []).filter((c: any) => (
                    !props.group ||
                    c.scheduled == null ||
                    (isCoverageForExtraDay(c, props.group) && c.planning_id === get(props, 'planningItem.guid'))
                )),
            attachments: (getAttachments(props.item)).length,
            isRecurring: isRecurring(props.item),
        };
    }

    render() {
        const props = this.props;
        const state = this.state;
        const className = bem('wire-articles', 'item__meta', {row: props.row});

        return (
            <div className={className}>
                <AgendaMetaTime
                    item={props.item}
                    borderRight={!props.isMobilePhone}
                    isRecurring={state.isRecurring}
                    group={props.group}
                    isMobilePhone={props.isMobilePhone}
                />

                {state.coveragesToDisplay.length > 0 && (
                    <div className='wire-articles__item__icons wire-articles__item__icons--dashed-border'>
                        {(state.coveragesToDisplay as Array<any>).map((coverage: any, index) => (
                            <AgendaListCoverageItem
                                key={index}
                                planningItem={props.planningItem}
                                user={props.user}
                                coverage={coverage}
                                showBorder={props.isMobilePhone == true && index === state.coveragesToDisplay.length - 1}
                                group={props.group}
                            />
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
