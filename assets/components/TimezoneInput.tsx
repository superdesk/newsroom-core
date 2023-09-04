import * as React from 'react';
import moment from 'moment-timezone';
import SelectInput, {ISelectInputProps} from './SelectInput';

type IProps = Omit<ISelectInputProps, 'options'>;

interface IState {
    timezones: Array<string>;
}

export class TimezoneInput extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {
            timezones: moment.tz.names(),
        };
    }

    render() {
        return (
            <SelectInput
                {...this.props}
                options={this.state.timezones.map((timezone) => ({
                    text: timezone,
                    value: timezone,
                }))}
            />
        );
    }
}
