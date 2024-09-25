import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import DatePicker from 'react-datepicker';
import format from 'date-fns/format';

import ExpiryButtonWrapper from './ExpiryButtonWrapper';

import {gettext} from '../utils';

const DatePickerComponent: React.ComponentType<any> = DatePicker;


export default class ExpiryDateInput extends React.Component<any, any> {
    static propTypes: any;
    options: any;
    constructor(props: any) {
        super(props);

        this.state = {value: !this.props.value ? 'never' : 'on'};

        this.options = [
            {text: gettext('on'), value: 'on'},
            {text: gettext('in 1 week'), value: '1 week'},
            {text: gettext('in 2 weeks'), value: '2 weeks'},
            {text: gettext('in 1 month'), value: '1 month'},
            {text: gettext('in 6 months'), value: '6 months'},
            {text: gettext('in 1 year'), value: '1 year'},
            {text: gettext('Never'), value: 'never'},
        ];

        this.onSelectChange = this.onSelectChange.bind(this);
        this.onDateChange = this.onDateChange.bind(this);
    }

    onSelectChange(event: any) {
        this.setState({value: event.target.value});
        let newDate: any;

        switch (event.target.value) {
        case '1 week':
            newDate = moment().add(1, 'week');
            break;
        case '2 weeks':
            newDate = moment().add(2, 'week');
            break;
        case '1 month':
            newDate = moment().add(1, 'month');
            break;
        case '6 months':
            newDate = moment().add(6, 'month');
            break;
        case '1 year':
            newDate = moment().add(1, 'year');
            break;
        }

        if (newDate) {
            this.props.onChange(newDate.format('YYYY-MM-DD'));
        } else {
            this.props.onChange('');
        }
    }

    onDateChange(newExpiry: any) {
        this.setState({value: 'on'});
        this.props.onChange(format(newExpiry, 'yyyy-MM-dd'));
    }

    render() {
        return (
            <div className="form-group expiry-date">
                <label htmlFor={this.props.name}>{this.props.label}</label>
                <div className="expiry-date__input-container">
                    <select
                        id={this.props.name}
                        name={this.props.name}
                        value={this.state.value}
                        onChange={this.onSelectChange}
                        className="form-control expiry-date__select-input"
                    >
                        {this.options.map((option: any) => {
                            return (
                                <option key={option.value} value={option.value}>{option.text}</option>
                            );
                        })}
                    </select>

                    <DatePickerComponent
                        dropdownMode="select"
                        disabled={this.state.value === 'never'}
                        customInput={<ExpiryButtonWrapper />}
                        dateFormat="dd MMMM yyyy"
                        todayButton={gettext('Today')}
                        selected={(this.props.value ? moment(this.props.value) : moment()).toDate()}
                        onChange={this.onDateChange}
                        highlightDates={[moment().toDate()]}
                        locale={window.locale || 'en'}
                        minDate={new Date()}
                        popperModifiers={[
                            {
                                name: 'offset',
                                options: {
                                    offset: [5, 10],
                                },
                            },
                        ]}
                    />
                </div>
                {this.props.error && (
                    <div className="alert alert-danger">{this.props.error}</div>
                )}
            </div>
        );
    }
}

ExpiryDateInput.propTypes = {
    label: PropTypes.string,
    name: PropTypes.string,
    value: PropTypes.string,
    error: PropTypes.arrayOf(PropTypes.string),
    onChange: PropTypes.func,
    required: PropTypes.bool,

    defaultOption: PropTypes.string,
};
