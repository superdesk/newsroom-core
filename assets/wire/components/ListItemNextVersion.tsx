import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import ItemVersion from './ItemVersion';
import {fetchNext, openItem} from '../actions';

class ListItemNextVersion extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any) {
        super(props);
        this.state = {next: null};
        this.open = this.open.bind(this);
        this.fetch(props);
    }

    componentWillReceiveProps(nextProps: any) {
        if (nextProps.item.nextversion !== this.props.item.nextversion) {
            this.fetch(nextProps);
        }
    }

    fetch(props: any) {
        props.dispatch(fetchNext(props.item))
            .then((next: any) => this.setState({next}))
            .catch(() => this.setState({next: null}));
    }

    open(version: any, event: any) {
        event.stopPropagation();
        this.props.dispatch(openItem(this.state.next));
    }

    render() {
        if (!this.state.next) {
            return null;
        }

        const baseClass = 'wire-column__preview';

        return (
            <div className={`${baseClass}__versions`}>
                <span className={`${baseClass}__versions__box-headline`}>
                    {gettext('Next version')}
                </span>

                <ItemVersion
                    version={this.state.next}
                    baseClass={baseClass}
                    onClick={this.open}
                    displayConfig={this.props.displayConfig}
                />
            </div>
        );
    }
}

ListItemNextVersion.propTypes = {
    item: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired,
    displayConfig: PropTypes.object,
};

const component: React.ComponentType<any> = connect()(ListItemNextVersion);

export default component;
