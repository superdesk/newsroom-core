import React from 'react';
import PropTypes from 'prop-types';
import {get, isEqual} from 'lodash';
import {bem} from 'ui/utils';
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

import {gettext} from 'utils';


class AgendaListItemIcons extends React.Component<any, any> {
    static propTypes: any;
    static defaultProps: any;
    constructor(props: any) {
        super(props);

        this.state = this.getUpdatedState(props);
    }

    itemChanged(nextProps: any) {
        return get(this.props, 'item._id') !== get(nextProps, 'item._id') ||
            get(this.props, 'item._etag') !== get(nextProps, 'item._etag') ||
            !isEqual(get(this.props, 'item.coverages'), get(nextProps, 'item.coverages'));
    }

    shouldComponentUpdate(nextProps: any) {
        return this.itemChanged(nextProps);
    }

    componentWillReceiveProps(nextProps: any) {
        if (this.itemChanged(nextProps)) {
            this.setState(this.getUpdatedState(nextProps));
        }
    }

    getUpdatedState(props: any) {
        return {
            internalNote: getInternalNote(props.item, props.planningItem),
            coveragesToDisplay: !hasCoverages(props.item) || props.hideCoverages ?
                [] :
                (props.item.coverages || []).filter((c: any) => (
                    !props.group ||
                    c.scheduled == null ||
                    (isCoverageForExtraDay(c) && c.planning_id === get(props, 'planningItem.guid'))
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
                        {state.coveragesToDisplay.map((coverage: any, index: any) => (
                            <AgendaListCoverageItem
                                key={index}
                                planningItem={props.planningItem}
                                user={props.user}
                                coverage={coverage}
                                showBorder={props.isMobilePhone && index === state.coveragesToDisplay.length - 1}
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

AgendaListItemIcons.propTypes = {
    item: PropTypes.object,
    planningItem: PropTypes.object,
    group: PropTypes.string,
    hideCoverages: PropTypes.bool,
    row: PropTypes.bool,
    isMobilePhone: PropTypes.bool,
    user: PropTypes.string,
};

AgendaListItemIcons.defaultProps = {isMobilePhone: false};

export default AgendaListItemIcons;
