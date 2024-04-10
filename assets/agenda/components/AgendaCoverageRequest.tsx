import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {gettext} from 'utils';
import {Button} from '../../components/Buttons';


class AgendaCoverageRequest extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any, context: any) {
        super(props, context);
        this.onRequestClick = this.onRequestClick.bind(this);
        this.reset = this.reset.bind(this);
        this.onMessageChange = this.onMessageChange.bind(this);
        this.requestCoverage = this.requestCoverage.bind(this);
        this.state = {opened: false, message: ''};
    }

    onRequestClick() {
        this.setState({opened: !this.state.opened});
    }

    reset() {
        this.setState({opened: false, message: '', status: null});
    }

    onMessageChange(event: any) {
        this.setState({message: event.target.value, status: null});
    }

    requestCoverage() {
        this.props.requestCoverage(this.props.item, this.state.message);
        this.reset();
    }

    render() {
        return (<div className='collapsible'>
            <a href='#' className='collapsible__link' onClick={this.onRequestClick}>
                <i className={classNames('icon-small--arrow-down me-1', {'rotate-90-ccw': !this.state.opened})}></i>
                <span>{gettext('Coverage inquiries')}</span>
            </a>
            <div className={classNames({'collapsible__form': !this.state.opened})}>
                <div className='form-group'>
                    <div className='field'>
                        <textarea
                            className='form-control'
                            placeholder={gettext('your inquiry')}
                            value={this.state.message}
                            onChange={this.onMessageChange}
                        ></textarea>
                    </div>
                </div>
                <div className='nh-button__group'>
                    <Button
                        value={gettext('Cancel')}
                        variant='secondary'
                        onClick={this.reset}
                    />
                    <Button
                        value={gettext('Submit inquiry')}
                        variant='primary'
                        disabled={!this.state.message}
                        onClick={this.requestCoverage}
                    />
                </div>
            </div>
        </div>);
    }

}

AgendaCoverageRequest.propTypes = {
    item: PropTypes.object,
    requestCoverage: PropTypes.func,
};

export default AgendaCoverageRequest;
