import React from 'react';

function Users() {
    return (
        <table className="table table-hover table--extended" tabIndex="-1">
            <thead>
                <tr>
                    <th>
                        <div>Name</div>
                        <div>Email</div>
                    </th>
                    <th>Status</th>
                    <th>Products</th>
                    <th>Status </th>
                    <th>
                        <div>Created on</div>
                        <div>Last active</div>
                    </th>                    
                </tr>
            </thead>
            <tbody>
                <tr className="table--selected" tabIndex="0">
                    <td>
                        <div className="name">Jacey Marks<label className="label label--green label--rounded label--fill">admin</label></div>
                        <div className="email">jacey.marks@mycompany.com</div>
                    </td>
                    <td><label className="label label--green label--rounded">active</label></td>
                    <td>Wire: <span className="badge rounded-pill bg-secondary text-dark">9</span></td>
                    <td>Agenda: <span className="badge rounded-pill bg-secondary text-dark">11</span></td>
                    <td>
                        <div className="time">Feb 10th, 2022 @ 12:16</div>
                        <div className="time">Aug 09th, 2022 @ 14:24</div>
                    </td>
                </tr>
                <tr className="" tabIndex="0">
                    <td>
                        <div className="name">Cannon Francis</div>
                        <div className="email">cannon.francis@mycompany.com</div>
                    </td>
                    <td><label className="label label--green label--rounded">active</label></td>
                    <td>Wire: <span className="badge rounded-pill bg-secondary text-dark">10</span></td>
                    <td>Agenda: <span className="badge rounded-pill bg-secondary text-dark">10</span></td>
                    <td>
                        <div className="time">Feb 10th, 2022 @ 12:16</div>
                        <div className="time">Aug 09th, 2022 @ 14:24</div>
                    </td>
                </tr>
                <tr className="" tabIndex="0">
                    <td>
                        <div className="name">Adrian Trujillo</div>
                        <div className="email">adrian.trujillo@mycompany.com</div>
                    </td>
                    <td><label className="label label--orange2 label--rounded">pending</label></td>
                    <td>Wire: <span className="badge rounded-pill bg-secondary text-dark">8</span></td>
                    <td>Agenda: <span className="badge rounded-pill bg-secondary text-dark">8</span></td>
                    <td>
                        <div className="time">Feb 10th, 2022 @ 12:16</div>
                        <div className="time">Aug 09th, 2022 @ 14:24</div>
                    </td>
                </tr>
                <tr className="" tabIndex="0">
                    <td>
                        <div className="name">Gillian Waller</div>
                        <div className="email">gillian.waller@mycompany.com </div>
                    </td>
                    <td><label className="label label--orange2 label--rounded">pending</label></td>
                    <td>Wire: <span className="badge rounded-pill bg-secondary text-dark">8</span></td>
                    <td>Agenda: <span className="badge badge--disabled rounded-pill bg-secondary text-dark">0</span></td>
                    <td>
                        <div className="time">Feb 10th, 2022 @ 12:16</div>
                        <div className="time">Aug 09th, 2022 @ 14:24</div>
                    </td>
                </tr>
            </tbody>
        </table>
    )
}

export default Users;